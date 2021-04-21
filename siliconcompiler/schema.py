# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.

import re
import os
import textwrap
import sys

###############################################################################
# CHIP CONFIGURATION
###############################################################################
def schema_cfg():
    '''Method for defining Chip configuration schema
    All the keys defined in this dictionary are reserved words.
    '''

    cfg = {}

    # Flow Setup (from schema_options)
    cfg = schema_flow(cfg, 'default')

    # Metric Tracking
    cfg = schema_metrics(cfg, 'goal')
    cfg = schema_metrics(cfg, 'real')    
    
    # Provenance Tracking
    cfg = schema_provenance(cfg) 
    
    # FPGA Parameters
    cfg = schema_fpga(cfg)

    # ASIC Parameters
    cfg = schema_pdk(cfg)
    cfg = schema_asic(cfg) 
    cfg = schema_libs(cfg, 'stdcell')
    cfg = schema_libs(cfg, 'macro')

    # Designer's Choice
    cfg = schema_design(cfg)
    cfg = schema_mcmm(cfg)
    
    # Designer Run options
    cfg = schema_options(cfg)

    # Run status
    cfg = schema_status(cfg)

    return cfg

###############################################################################
# CHIP LAYOUT
###############################################################################
def schema_layout():
    
    layout = {}

    layout = schema_lef(layout)

    layout = schema_def(layout)

    return layout

###############################################################################
# UTILITY FUNCTIONS TIED TO SC SPECIFICATIONS
###############################################################################

def schema_path(filename):
    ''' Resolves file paths using SCPATH and resolve environment variables
    starting with $
    '''

    #Resolve absolute path usign SCPATH
    #list is read left to right    
    scpaths = str(os.environ['SCPATH']).split(':')
    for searchdir in scpaths:        
        abspath = searchdir + "/" + filename
        if os.path.exists(abspath):
            filename = abspath
            break
    #Replace $ Variables
    varmatch = re.match('^\$(\w+)(.*)', filename)
    if varmatch:
        var = varmatch.group(1)
        varpath = os.getenv(var)
        if varpath is None:
            print("FATAL ERROR: Missing environment variable:", var)
            sys.exit()
        relpath = varmatch.group(2)
        filename = varpath + relpath

    #Check Path Validity
    if not os.path.exists(filename):
        print("FATAL ERROR: File/Dir not found:", filename)
        sys.exit()
        
    return filename
            
def schema_istrue(value):
    ''' Checks schema boolean string and returns Python True/False
    '''
    boolean = value[-1].lower()
    if boolean == "true":
        return True
    else:
        return False

    
###############################################################################
# FPGA
###############################################################################

def schema_fpga(cfg):
    ''' FPGA Setup
    '''
    cfg['fpga'] = {}

    cfg['fpga']['xml'] = {
        'switch' : '-fpga_xml',
        'requirement' : 'fpga',
        'type' : ['file'],
        'defvalue' : [],
        'short_help' : 'FPGA Architecture File',
        'param_help' : "'fpga' 'xml' <file>",
        'example': ["cli: -fpga_xml myfpga.xml",                    
                    "api:  chip.set('fpga', 'xml', 'myfpga.xml')"],
        'help' : """
        Provides an XML-based architecture description for the target FPGA
        architecture to be used in VTR, allowing targeting a large number of 
        virtual and commercial architectures.
        [More information...](https://verilogtorouting.org)
        """
    }

    cfg['fpga']['vendor'] = {
        'switch' : '-fpga_vendor',
        'requirement' : '!fpga_xml',
        'type' : ['str'],
        'defvalue' : [],
        'short_help' : 'FPGA Vendor Name',
        'param_help' : "'fpga' 'vendor' <str>",
        'example': ["cli: -fpga_vendor acme",                    
                    "api:  chip.set('fpga', 'vendor', 'acme')"],
        'help' : """
        Name of the FPGA vendor for non-VTR based compilation
        """
    }

    cfg['fpga']['device'] = {
        'switch' : '-fpga_device',
        'requirement' : '!fpga_xml',
        'type' : ['str'],
        'defvalue' : [],
        'short_help' : 'FPGA Device Name',
        'param_help' : "'fpga' 'device' <str>",
        'example': ["cli: -fpga_device fpga64k",                    
                    "api:  chip.set('fpga', 'device', 'fpga64k')"],
        'help' : """
        Name of the FPGA device for non-VTR based compilation
        """
    }

    return cfg

###############################################################################
# PDK
###############################################################################

def schema_pdk(cfg):
    ''' Process Design Kit Setup
    '''
    cfg['pdk'] = {}
    cfg['pdk']['foundry'] = {
        'switch' : '-pdk_foundry',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Foundry Name',
        'param_help' : "'pdk' 'foundry' <str>",
        'example': ["cli: -pdk_foundry virtual",                    
                    "api:  chip.set('pdk', 'foundry', 'virtual')"],
        'help' : """
        The name of the foundry. For example: intel, gf, tsmc, "samsung, 
        skywater, virtual. The \'virtual\' keyword is reserved for simulated 
        non-manufacturable processes such as freepdk45 and asap7.              
        """        
    }

    cfg['pdk']['process'] = {
        'switch' : '-pdk_process',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Process Name',
        'param_help' : "'pdk' 'process' <str>",
        'example': ["cli: -pdk_process asap7",                    
                    "api:  chip.set('pdk', 'process', 'asap7')"],
        'help' : """
        The official public name of the foundry process. The name is case 
        insensitive, but should otherwise match the complete public process 
        name from the foundry. Example process names include 22ffl from Intel,
        12lpplus from Globalfoundries, and 16ffc from TSMC.        
        """
    }

    cfg['pdk']['node'] = {
        'switch' : '-pdk_node',
        'requirement' : 'asic',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Process Node',
        'param_help' : "'pdk' 'node' <num>",
        'example': ["cli: -pdk_node 130",                    
                    "api:  chip.set('pdk', 'node', '130')"],
        'help' : """
        An approximate relative minimum dimension of the process node. A 
        required parameter in some reference flows that leverage the value to 
        drive technology dependent synthesis and APR optimization. Node 
        examples include 180nm, 130nm, 90nm, 65nm, 45nm, 32nm, 22nm, 14nm, 
        10nm, 7nm, 5nm, 3nm. The value entered implies nanometers.
        """
    }

    cfg['pdk']['rev'] = {
        'switch' : '-pdk_rev',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Process Revision',
        'param_help' : "'pdk' 'rev' <str>",
        'example': ["cli: -pdk_rev 1.0",                    
                    "api:  chip.set('pdk', 'rev', '1.0')"],
        'help' : """
        An alphanumeric string specifying the revision  of the current PDK. 
        Verification of correct PDK and IP revisions revisions is an ASIC 
        tapeout requirement in all commercial foundries.
        """
    }
    
    cfg['pdk']['drm'] = {
        'switch' : '-pdk_drm',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],        
        'short_help' : 'PDK Design Rule Manual',
        'param_help' : "'pdk' 'drm' <file>",
        'example': ["cli: -pdk_drm asap7_drm.pdf",                    
                    "api:  chip.set('pdk', 'drm', 'asap7_drm.pdf')"],
        'help' : """
        A PDK document that includes complete information about physical and 
        electrical design rules to comply with in the design and layout of the 
        chip. In cases where the user guides and design rules are combined into
        a single document, the pdk_doc parameter can be left blank.
        """
    }

    cfg['pdk']['doc'] = {
        'switch' : '-pdk_doc',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'PDK Documents',
        'param_help' : "'pdk' 'doc' <file>",
        'example': ["cli: -pdk_doc asap7_userguide.pdf",                    
                    "api: chip.add('pdk', 'doc', 'asap7_userguide.pdf')"],
        'help' : """
        A list of critical PDK designer documents provided by the foundry 
        entered in order of priority. The first item in the list should be the
        primary PDK user guide. The purpose of the list is to serve as a 
        central record for all must-read PDK documents.
        """
    }
        
    cfg['pdk']['stackup'] = {
        'switch' : '-pdk_stackup',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Process Metal Stackups',
        'param_help' : "'pdk' 'stackup' <str>",
        'example': ["cli: -pdk_stackup 2MA4MB2MC",                    
                    "api: chip.add('pdk', 'tackup', '2MA4MB2MC')"],
        'help' : """
        A list of all metal stackups offered in the process node. Older process
        nodes may only offer a single metal stackup, while advanced nodes 
        offer a large but finite list of metal stacks with varying combinations
        of metal line pitches and thicknesses. Stackup naming is unqiue to a 
        foundry, but is generally a long string or code. For example, a 10 
        metal stackup two 1x wide, four 2x wide, and 4x wide metals, might be
        identified as 2MA4MB2MC. Each stackup will come with its own set of 
        routing technology files and parasitic models specified in the 
        pdk_pexmodel and pdk_aprtech parameters.
        """
    }

    cfg['pdk']['devicemodel'] = {}
    cfg['pdk']['devicemodel']['default'] = {}
    cfg['pdk']['devicemodel']['default']['default'] = {}
    cfg['pdk']['devicemodel']['default']['default']['default'] = {
        'switch' : '-pdk_devicemodel',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Device Models',
        'param_help' : "'pdk' 'devicemodel' stackup type tool <file>",
        'example': ["""cli: -pdk_devicemodel 'M10 spice xyce asap7.sp'""",
                    """api: chip.add('pdk','devicemodel','M10','spice','xyce',
                    'asap7.sp')"""],
        'help' : """
        Filepaths for all PDK device models. The structure serves as a central 
        access registry for models for different purpose and tools. Examples of
        device model types include spice, aging, electromigration, radiation. 
        An example of a spice tool is xyce.
        """
    }

    cfg['pdk']['pexmodel'] = {}
    cfg['pdk']['pexmodel']['default'] = {}
    cfg['pdk']['pexmodel']['default']['default']= {}
    cfg['pdk']['pexmodel']['default']['default']['default'] = {
        'switch' : '-pdk_pexmodel',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Parasitic TCAD Models',
        'param_help' : "'pdk' 'pexmodel' stackup corner tool <file>",
        'example': ["""cli: -pdk_pexmodel 'stack10 max fastcap wire.mod'""",
                    """api: chip.add('pdk','pexmodel','stack10','max','fastcap'
                    'wire.mod')"""],
        'help' : """
        Filepaths for all PDK wire TCAD models. The structure serves as a 
        central access registry for models for different purpose and tools. 
        Examples of RC extraction corners include: min, max, nominal. An 
        example of an extraction tool is FastCap.
        """
    }

    cfg['pdk']['layermap'] = {}
    cfg['pdk']['layermap']['default'] = {}
    cfg['pdk']['layermap']['default']['default'] = {}
    cfg['pdk']['layermap']['default']['default']['default'] = {
        'switch' : '-pdk_layermap',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Mask Layer Maps',
        'param_help' : "'pdk' 'layermap' stackup src dst <file>",
        'example': ["""cli: -pdk_layermap 'M10 klayout gds asap7.map'""",
                    """api: chip.add('pdk','layermap','M10','klayout','gds'
                    'asap7.map')"""],
        'help' : """
        Files describing input/output mapping for streaming layout data from 
        one format to another. A foundry PDK will include an official layer 
        list for all user entered and generated layers supported in the GDS 
        accepted by the foundry for processing, but there is no standardized 
        layer definition format that can be read and written by all EDA tools.
        To ensure mask layer matching, key/value type mapping files are needed
        to convert EDA databases to/from GDS and to convert between different
        types of EDA databases.
        """
    }

    cfg['pdk']['display'] = {}
    cfg['pdk']['display']['default'] = {}
    cfg['pdk']['display']['default']['default'] = {
        'switch' : '-pdk_display',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Display Configurations',
        'param_help' : "'pdk' 'display' stackup tool <file>",
        'example': ["""cli: -pdk_display 'stack10 klayout display.cfg'""",
                    """api: chip.add('pdk', display','stack10','klayout',
                    'display.cfg')"""],
        'help' : """
        Display configuration files describing colors and pattern schemes for
        all layers in the PDK. The display configuration file is entered on a 
        stackup and per tool basis.
        """
    }

    cfg['pdk']['plib'] = {}
    cfg['pdk']['plib']['default'] = {}
    cfg['pdk']['plib']['default']['default'] = {
        'switch' : '-pdk_plib',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Primitive Libraries',
        'param_help' : "'pdk' 'plib' stackup format <file>",
        'example': ["""cli: -pdk_plib 'stack10 oa /disk/asap7/oa/devlib'""",
                    """api: chip.add('pdk','plib','stack10','oa', 
                    '/disk/asap7/oa/devlib')"""],
        'help' : """
        Filepaths to all primitive cell libraries supported by the PDK. The 
        filepaths are entered on a per stackup and per format basis.
        """
    }

    cfg['pdk']['aprtech'] = {}
    cfg['pdk']['aprtech']['default'] = {}
    cfg['pdk']['aprtech']['default']['default'] = {}
    cfg['pdk']['aprtech']['default']['default']['default'] = {
        'switch' : '-pdk_aprtech',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'APR Technology File',
        'param_help' : "'pdk' 'aprtech' stackup libtype vendor <file>",
        'example': ["""cli: -pdk_aprtech 'stack10 12t openroad tech.lef'""",
                    """api: chip.add('pdk','aprtech','stack10','12t','openroad',
                    'tech.lef')"""],
        'help' : """
        Technology file containing the design rule and setup information needed
        to enable DRC clean automated placement a routing. The file is 
        specified on a per stackup, libtype, and format basis, where libtype 
        generates the library architecture (e.g. library height). For example a
        PDK with support for 9 and 12 track libraries might have libtypes 
        called 9t and 12t.
        """
    }

    cfg['pdk']['aprlayer'] = {}
    cfg['pdk']['aprlayer']['default'] = {}
    cfg['pdk']['aprlayer']['default']['default'] = {}    

    #Name Map
    cfg['pdk']['aprlayer']['default']['default']['name'] = {
        'switch' : '-pdk_aprlayer_name',
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'APR Layer Name Map',
        'param_help' : "'pdk' 'aprlayer' stackup metal 'name' <str>",
        'example': ["""cli: -pdk_aprlayer_name 'stack10 m1 metal1'""",
                    """api: chip.add('pdk', 'aprlayer', 'stack10', 'm1', 'name',
                    'metal1')"""],
        'help' : """
        Defines the hardcoded PDK metal name on a per stackup and per metal 
        basis. Metal layers are ordered from m1 to mn, where m1 is the lowest
        routing layer in the tech.lef.
        """
    }
    # Horozontal Routing Grid
    cfg['pdk']['aprlayer']['default']['default']['hgrid'] = {
        'switch' : '-pdk_aprlayer_hgrid',
        'requirement' : 'optional',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'APR Layer Horizontal Grid',
        'param_help' : "'pdk' 'aprlayer' stackup metal 'hgrid'",
        'example': ["""cli: -pdk_aprlayer_hgrid 'stack10 m1 0.5'""",
                    """api: chip.add('pdk','aprlayer','stack10','m1','hgrid',
                    '0.5')"""],
        'help' : """
        Defines the horizontal routing grid on a a per stackup and per metal 
        basis. Values are specified in um. Metal layers are ordered from m1 to 
        mn, where m1 is the lowest routing layer in the tech.lef.        
        """
    }

    # Vertical Routing Grid
    cfg['pdk']['aprlayer']['default']['default']['vgrid'] = {
        'switch' : '-pdk_aprlayer_vgrid',
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'APR Layer Vertical Grid',
        'param_help' : "'pdk' 'aprlayer' stackup metal 'vgrid'",
        'example': ["""cli: -pdk_aprlayer_vgrid 'stack10 m2 0.5'""",
                    """api: chip.add('pdk','aprlayer','stack10','m2','vgrid',
                    '0.5')"""],
        'help' : """
        Defines the vertical routing grid on a a per stackup and per metal 
        basis. Values are specified in um. Metal layers are ordered from m1 to
        mn, where m1 is the lowest routing layer in the tech.lef.
        """
    }
    # Horizontal Grid Offset
    cfg['pdk']['aprlayer']['default']['default']['hoffset'] = {
        'switch' : '-pdk_aprlayer_hoffset',
        'requirement' : 'optional',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'APR Layer Preferred Direction',
        'param_help' : "'pdk' 'aprlayer' stackup metal 'hoffset'",
        'example': ["""cli: -pdk_aprlayer_hoffset 'stack10 m2 0.5'""",
                    """api: chip.add('pdk','aprlayer','stack10','m2','hoffset',
                    '0.5')"""],
        'help' : """
        Defines the horizontal grid offset of a metal layer specified on a per 
        stackup and per metal basis. Values are specified in um.
        """
    }
    # Vertical Grid Offset
    cfg['pdk']['aprlayer']['default']['default']['voffset'] = {
        'switch' : '-pdk_aprlayer_voffset',
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'APR Layer Preferred Direction',
        'param_help' : "'pdk' 'aprlayer' stackup metal 'voffset'",
        'example': ["""cli: -pdk_aprlayer_hoffset 'stack10 m2 0.5'""",
                    """api: chip.add('pdk','aprlayer','stack10','m2','voffset',
                    '0.5')"""],
        'help' : """
        Defines the vertical grid offset of a metal layer specified on a per 
        stackup and per metal basis. Values are specified in um.
        """
    }
    
    cfg['pdk']['tapmax'] = {
        'switch' : '-pdk_tapmax',
        'requirement' : 'apr',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [], 
        'short_help' : 'Tap Cell Max Distance Rule',
        'param_help' : "'pdk' 'tapmax' <num>",
        'example': ["""cli: -pdk_tapmax 100""",
                    """api: chip.set('pdk', 'tapmax','100')"""],
        'help' : """
        Maximum distance allowed between tap cells in the PDK. The value is 
        required for automated place and route and is entered in micrometers.
        """
    }

    cfg['pdk']['tapoffset'] = {
        'switch' : '-pdk_tapoffset',
        'requirement' : 'apr',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Tap Cell Offset Rule',
        'param_help' : "'pdk' 'tapoffset' <num>",
        'example': ["""cli: -pdk_tapoffset 100""",
                    """api: chip.set('pdk, 'tapoffset','100')"""],
        'help' : """
        Offset from the edge of the block to the tap cell grid. 
        The value is required for automated place and route and is entered in 
        micrometers.
        """
    }

    return cfg

###############################################################################
# Library Configuration
###############################################################################

def schema_libs(cfg, group):

    cfg[group] = {}

    cfg[group]['default'] = {}

    cfg[group]['default']['rev'] = {
        'switch' : '-'+group+'_rev',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' :  group.capitalize() + ' Release Revision',
        'param_help' : "'"+group+"' libname 'rev' <str>",
        'example': ["cli: -"+group+"_rev 'mylib 1.0",
                    "api: chip.set('"+group+"','mylib','rev','1.0')"],
        'help' : """ 
        String specifying revision on a per library basis. Verification of 
        correct PDK and IP revisions is an ASIC tapeout requirement in all 
        commercial foundries.
        """
    }

    cfg[group]['default']['origin'] = {
        'switch' : '-'+group+'_origin',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' :  group.capitalize() + ' Origin',
        'param_help' : "'"+group+"' libname 'origin' <str>",
        'example': ["cli: -"+group+"_origin 'mylib US",
                    "api: chip.set('"+group+"','mylib','origin','US')"],
        'help' : """
        String specifying library country of origin.
        """
    }

    cfg[group]['default']['license'] = {
        'switch' : '-'+group+'_license',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' :  group.capitalize() + ' License File',
        'param_help' : "'"+group+"' libname 'license' <file>",
        'example': ["cli: -"+group+"_license 'mylib ./LICENSE",
                    "api: chip.set('"+group+"','mylib','license','./LICENSE')"],
        'help' : """
        Filepath to library license
        """        
    }
    
    cfg[group]['default']['doc'] = {
        'switch' : '-'+group+'_doc',
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' :  group.capitalize() + ' Documentation',
        'param_help' : "'"+group+"' libname 'doc' <file>",
        'example': ["cli: -"+group+"_doc 'lib lib_guide.pdf",
                    "api: chip.set('"+group+"','lib','doc','lib_guide.pdf"],
        'help' : """
        A list of critical library documents entered in order of importance. 
        The first item in thelist should be the primary library user guide. 
        The  purpose of the list is to serve as a central record for all
        must-read PDK documents
        """
    }

    cfg[group]['default']['datasheet'] = {
        'switch' : '-'+group+"_datasheet",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' Datasheets',
        'param_help' : "'"+group+"' libname 'datasheet' <file>",
        'example': ["cli: -"+group+"_datasheet 'lib lib_ds.pdf",
                    "api: chip.set('"+group+"','lib','datasheet','lib_ds.pdf/"],
        'help' : """
        A complete collection of library datasheets. The documentation can be
        provied as a PDF or as a filepath to a directory with one HTMl file 
        per cell. This parameter is optional for libraries where the datsheet
        is merged within the library integration document.
        """
    }

    cfg[group]['default']['libtype'] = {
        'switch' : '-'+group+'_libtype',
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Type',
        'param_help' : "'"+group+"' libname 'libtype' <str>",
        'example': ["cli: -"+group+"_libtype 'mylib 12t",
                    "api: chip.set('"+group+"','mylib','libtype', '12t'"],
        'help' : """
        Libtype is a a unique string that identifies the row height or
        performance class of the library for APR. The libtype must match up
        with the name used in the pdk_aprtech dictionary. Mixing of libtypes
        in a flat place and route block is not allowed.
        """
    }

    cfg[group]['default']['width'] = {
        'switch' : '-'+group+'_width',
        'requirement' : 'apr',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Width',
        'param_help' : "'"+group+"' libname 'width' <num>",
        'example': ["cli: -"+group+"_width 'mylib 0.1""",
                    "api: chip.set('"+group+"','mylib','width', '0.1'"],
        
        'help' : """
        Specifies the width of a unit cell. The value can usually be
        extracted automatically from the layout library but is included in the
        schema to simplify the process of creating parametrized floorplans.
        """
    }

    cfg[group]['default']['height'] = {
        'switch' : '-'+group+'_height',
        'requirement' : 'apr',
        'type' : ['num'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Height',
        'param_help' : "'"+group+"' libname 'height' <num>",
        'example': ["cli: -"+group+"_height 'mylib 1.0""",
                    "api: chip.set('"+group+"','mylib','height', '1.0'"],
        'help' : """
        Specifies the height of a unit cell. The value can usually be
        extracted automatically from the layout library but is included in the
        schema to simplify the process of creating parametrized floorplans.
        """
    }
    
    ###############################
    #Models (Timing, Power, Noise)
    ###############################

    cfg[group]['default']['model'] = {}
    cfg[group]['default']['model']['default'] = {}

    #Operating Conditions (per corner)
    cfg[group]['default']['model']['default']['opcond'] = {
        'switch' : '-'+group+"_opcond",
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Operating Condition',
        'param_help' : "'"+group+"' libname 'model' corner 'opcond' <str>",
        'example':["cli: -"+group+"_opcond 'lib model ss_1.0v_125c WORST'",
                   "api: chip.add('"+group+"','lib','model','ss_1.0v_125c', \
                   'opcond', 'WORST'"],
        'help' : """
        The default operating condition to use for mcmm optimization and
        signoff on a per corner basis.
        """
    }
        
    #Checks To Do (per corner)
    cfg[group]['default']['model']['default']['check'] = {
        'switch' : '-'+group+"_check",
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Corner Checks',
        'param_help' : "'"+group+"' libname 'model' corner 'check' <str>",
        'example':["cli: -"+group+"_check 'lib model ss_1.0v_125c setup'",
                   "api: chip.add('"+group+"','lib','model','ss_1.0v_125c', \
                   'check', 'setup'"],
        'help' : """
        Per corner checks to perform during optimization and STA signoff.
        Names used in the 'mcmm' scenarios must align with the 'check' names
        used in this dictionary. The purpose of the dictionary is to serve as 
        a serve as a central record for the PDK/Library recommended corner 
        methodology and all PVT timing corners supported. Standard 'check' 
        values include setup, hold, power, noise, reliability but can be 
        extended based on eda support and methodology.
        """
    }
        
    #NLDM
    cfg[group]['default']['model']['default']['nldm'] = {}
    cfg[group]['default']['model']['default']['nldm']['default'] = {        
        'switch' : '-'+group+"_nldm",
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' NLDM Timing Model',
        'param_help' : "'"+group+"' libname 'model' corner 'nldm' type <file>",
        'example':["cli: -"+group+"_nldm 'lib model ss lib.gz lib_ss.lib.gz'",
                   "api: chip.add('"+group+"','lib','model','ss','nldm', \
                   'lib.gz', 'lib_ss.lib.gz'"],
        'help' : """
        Filepaths to NLDM models. Timing files are specified on a per lib,
        per corner, and per format basis. The format is driven by EDA tool
        requirements. Examples of legal formats includ: lib, lib.gz, lib.bz2, 
        and ldb.            
        """
    }

    #CCS
    cfg[group]['default']['model']['default']['ccs'] = {}
    cfg[group]['default']['model']['default']['ccs']['default'] = {        
        'switch' : '-'+group+"_ccs",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' CCS Timing Model',
        'param_help' : "'"+group+"' libname 'model' corner 'ccs' type <file>",
        'example':["cli: -"+group+"_ccs 'lib model ss lib.gz lib_ss.lib.gz'",
                   "api: chip.add('"+group+"','lib','model','ss', 'ccs', \
                   'lib.gz', 'lib_ss.lib.gz'"],
        'help' : """
        Filepaths to CCS models. Timing files are specified on a per lib,
        per corner, and per format basis. The format is driven by EDA tool
        requirements. Examples of legal formats includ: lib, lib.gz, lib.bz2, 
        and ldb.            
        """
     }

    #SCM
    cfg[group]['default']['model']['default']['scm'] = {}
    cfg[group]['default']['model']['default']['scm']['default'] = {        
        'switch' : '-'+group+"_scm",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' SCM Timing Model',
        'param_help' : "'"+group+"' libname 'model' corner 'scm' type <file>",
        'example':["cli: -"+group+"_scm 'lib model ss lib.gz lib_ss.lib.gz'",
                   "api: chip.add('"+group+"','lib','model','ss', 'scm', \
                   'lib.gz', 'lib_ss.lib.gz'"],
        'help' : """
        Filepaths to SCM models. Timing files are specified on a per lib,
        per corner, and per format basis. The format is driven by EDA tool
        requirements. Examples of legal formats includ: lib, lib.gz, lib.bz2, 
        and ldb.            
        """
    }
        
    #AOCV
    cfg[group]['default']['model']['default']['aocv'] = {        
        'switch' : '-'+group+"_aocv",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' AOCV Timing Model',
        'param_help' : "'"+group+"' libname 'model' corner 'aocv' <file>",
        'example':["cli: -"+group+"_aocv 'lib model ss lib.aocv'",
                   "api: chip.add('"+group+"','lib','model','ss', 'aocv', \
                   'lib_ss.aocv'"],
        'help': """
        Filepaths to AOCV models. Timing files are specified on a per lib,
        per corner basis. 
        """
    }

    #APL
    cfg[group]['default']['model']['default']['apl'] = {}
    cfg[group]['default']['model']['default']['apl']['default'] = {        
        'switch' : '-'+group+"_apl",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' APL Power Model',
        'param_help' : "'"+group+"' libname 'model' corner 'apl' type <file>",
        'example':["cli: -"+group+"_apl 'lib model ss cdev lib_tt.cdev'",
                   "api: chip.add('"+group+"','lib','model','ss','apl','cdev',\
                   'lib_tt.cdev'"],
        'help' : """
        Filepaths to APL power models. Power files are specified on a per
        lib, per corner, and per format basis.
        """
    }

    #LEF
    cfg[group]['default']['lef'] = {
        'switch' : '-'+group+"_lef",
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' LEF',
        'param_help' : "'"+group+"' libname 'lef' <file>",
        'example':["cli: -"+group+"_lef 'mylib mylib.lef'",
                   "api: chip.add('"+group+"','mylib','lef','mylib.lef')"],
        'help' : """
        An abstracted view of library cells that gives a complete description
        of the cell's place and route boundary, pin positions, pin metals, and
        metal routing blockages.
        """
    }
    
    #GDS
    cfg[group]['default']['gds'] = {
        'switch' : '-'+group+"_gds",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' GDS',
        'param_help' : "'"+group+"' libname 'gds' <file>",
        'example':["cli: -"+group+"_gds 'mylib mylib.gds'",
                   "api: chip.add('"+group+"','mylib','gds','mylib.gds')"],
        'help' : """
        The complete mask layout of the library cells ready to be merged with
        the rest of the design for tapeout. In some cases, the GDS merge 
        happens at the foundry, so inclusion of CDL files is optional. In all 
        cases, where the CDL are available they should specified here to 
        enable LVS checks pre tapout                                     
        """
    }

    cfg[group]['default']['cdl'] = {
        'switch' : '-'+group+"_cdl",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' CDL Netlist',
        'param_help' : "'"+group+"' libname 'cdl' <file>",
        'example':["cli: -"+group+"_cdl 'mylib mylib.cdl'",
                   "api: chip.add('"+group+"','mylib','cdl','mylib.cdl')"],
        'help' : """
        Files containing the netlists used for layout versus schematic (LVS)
        checks. In some cases, the GDS merge happens at the foundry, so
        inclusion of a CDL file is optional. In all cases, where the CDL
        files are available they should specified here to enable LVS checks
        pre tapout
        """                                                          
    }
    cfg[group]['default']['spice'] = {}
    cfg[group]['default']['spice']['default'] = {
        'switch' : '-'+group+"_spice",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' Spice Netlist',
        'param_help' : "'"+group+"' libname 'spice' 'format' <file>",
        'example':["cli: -"+group+"_spice 'mylib pspice mylib.sp'",
                   "api: chip.add('"+group+"','mylib','spice', 'pspice',\
                   'mylib.sp')"],
        'help' : """
        Files containing library spice netlists used for circuit 
        simulation, specified on a per format basis. 
        """
    }
    cfg[group]['default']['hdl'] = {}
    cfg[group]['default']['hdl']['default'] = {
        'switch' : '-'+group+"_hdl",
        'requirement' : 'asic',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' HDL Model',
        'param_help' : "'"+group+"' libname 'hdl' 'format' <file>",
        'example':["cli: -"+group+"_hdl 'mylib verilog mylib.v'",
                   "api: chip.add('"+group+"','mylib','hdl', 'verilog',\
                   'mylib.v')"],
        'help' : """
        Library HDL models, specifed on a per format basis.
        """
    }
    
    cfg[group]['default']['atpg'] = {
        'switch' : '-'+group+"_atpg",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' ATPG Model',
        'param_help' : "'"+group+"' libname 'atpg' <file>",
        'example':["cli: -"+group+"_atpg 'mylib atpg mylib.atpg'",
                   "api: chip.add('"+group+"','mylib','atpg','mylib.atpg')"],
        'help' : """
        Library models used for ATPG based automated faultd based post
        manufacturing testing.                                        
        """
    }

    cfg[group]['default']['pgmetal'] = {
        'switch' : '-'+group+"_pgmetal",
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Power/Ground Layer',
        'param_help' : "'"+group+"' libname 'pgmetal' <str>",
        'example':["cli: -"+group+"_pgmetal 'mylib pgmetal m1'",
                   "api: chip.add('"+group+"','mylib','pgmetal','m1')"],
        'help' : """
        Specifies the top metal layer used for power and ground routing within
        the library. The parameter can be used to guide cell power grid hookup
        by APR tools.
        """
    }

    cfg[group]['default']['tag'] = {
        'switch' : '-'+group+"_tag",
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Identifier Tags',
        'param_help' : "'"+group+"' libname 'tag' <str>",
        'example':["cli: -"+group+"_tag 'mylib virtual'",
                   "api: chip.add('"+group+"','mylib','tag','virtual')"],
        'help' : """
        Marks a library with a set of tags that can be used by the designer
        and EDA tools for optimization purposes. The tags are meant to cover
        features not currently supported by built in EDA optimization flows,
        but which can be queried through EDA tool TCL commands and lists.
        The example below demonstrates tagging the whole library as virtual.
        """
    }

    cfg[group]['default']['driver'] = {
        'switch' : '-'+group+"_driver",
        'requirement' : 'asic',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Default Driver Cell',
        'param_help' : "'"+group+"' libname 'driver' <str>",
        'example':["cli: -"+group+"_driver 'mylib BUFX1'",
                   "api: chip.add('"+group+"','mylib','driver','BUFX1')"],
        'help' : """
        The name of a library cell to be used as the default driver for
        block timing constraints. The cell should be strong enough to drive
        a block input from another block including wire capacitance.
        In cases where the actual driver is known, the actual driver cell
        should be used.
        """
    }

    cfg[group]['default']['site'] = {
        'switch' : '-'+group+"_site",
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Site/Tile Name',
        'param_help' : "'"+group+"' libname 'site' <str>",
        'example':["cli: -"+group+"_site 'mylib core'",
                   "api: chip.add('"+group+"','mylib','site','core')"],
        'help' : """
        Provides the primary site name to use for placement.
        """
    }

    cfg[group]['default']['cells'] = {}
    cfg[group]['default']['cells']['default'] = {
        'switch' : '-'+group+"_cells",
        'requirement' : 'optional',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : group.capitalize() + ' Cell Lists',
        'param_help' : "'"+group+"' libname 'cells' celltype <str>",
        'example':["cli: -"+group+"_cells 'mylib dontuse *eco*'",
                   "api: chip.add('"+group+"','mylib','cells','dontuse', \
                   '*eco*')"],
        'help' : """
        A named list of cells grouped by a property that can be accessed
        directly by the designer and EDA tools. The example below shows how
        all cells containing the string 'eco' could be marked as dont use
        for the tool.
        """
    }

    cfg[group]['default']['layoutdb'] = {}
    cfg[group]['default']['layoutdb']['default'] = {}
    cfg[group]['default']['layoutdb']['default']['default'] = {
        'switch' : '-'+group+"_layoutdb",
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : group.capitalize() + ' Layout Database',
        'param_help' : "'"+group+"' libname 'layoutdb' stackup format <file>",
        'example':["cli: -"+group+"_layoutdb 'mylib stack10 oa /disk/mulibdb",
                   "api: chip.add('"+group+"','mylib','layoutdb','stack10', \
                   'oa', '/disk/mylibdb')"],
        'help' : """
        Filepaths to compiled library layout database specified on a per format
        basis. Example formats include oa, mw, ndm.
        """
    }

    return cfg

###############################################################################
# Flow Configuration
###############################################################################

def schema_flow(cfg, step):

    if not 'flow' in cfg:
        cfg['flow'] = {}    
    cfg['flow'][step] = {}

    
    # Used to define flow sequence
    cfg['flow'][step]['input'] = {
        'switch' : '-flow_input',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Excution Dependency',
        'param_help' : "'flow' step 'input' <str>",
        'example': ["cli: -flow_input cts place",                    
                    "api:  chip.set('flow', 'cts', 'input', 'place'"],
        'help' : """
        Specifies the list of inputs dependanices to start 'step' execution.
        """
    }

    # exe
    cfg['flow'][step]['exe'] = {
        'switch' : '-flow_exe',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Executable Name',
        'param_help' : "'flow' step 'exe' <str>",
        'example': ["cli: -flow_exe cts openroad",                    
                    "api:  chip.set('flow', 'cts', 'exe', 'openroad'"],
        'help' : """
        The name of the exuctable step or the full path to the executable 
        specified on a per step basis.
        """
    }
    
    # exe version    
    cfg['flow'][step]['version'] = {
        'switch' : '-flow_version',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Executable Version',
        'param_help' : "'flow' step 'version' <str>",
        'example': ["cli: -flow_version cts 1.0",                    
                    "api:  chip.set('flow', 'cts', 'version', '1.0'"],
        'help' : """
        The version of the executable step to use in compilation.Mismatch 
        between the step specifed and the step avalable results in an error.
        """
    }
    
    #opt
    cfg['flow'][step]['option'] = {
        'switch' : '-flow_opt',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Executable Options',
        'param_help' : "'flow' step 'option' <str>",
        'example': ["cli: -flow_opt cts -no_init",                    
                    "api:  chip.set('flow', 'cts', 'opt', '-no_init'"],
        'help' : """
        A list of command line options for the executable. For multiple 
        argument options, enter each argument and value as a one list entry, 
        specified on a per step basis. Command line values must be enclosed in 
        quotes.
        """
    }
    
    #refdir
    cfg['flow'][step]['refdir'] = {
        'switch' : '-flow_refdir',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Reference Directory',
        'param_help' : "'flow' step 'refdir' <file>",
        'example': ["cli: -flow_refdir cts ./myrefdir",                    
                    "api:  chip.set('flow', 'cts', 'refdir', './myrefdir'"],
        'help' : """
        A path to a directory containing compilation scripts used by the 
        executable specified on a per step basis.
        """
    }
    
    #entry point script
    cfg['flow'][step]['script'] = {
        'switch' : '-flow_script',
        'requirement' : 'optional',
        'type' : ['file'],
        'lock' : 'false',
        'defvalue' : [],
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],   
        'short_help' : 'Entry Point script',
        'param_help' : "'flow' step 'script' <file>",
        'example': ["cli: -flow_script cts /myrefdir/cts.tcl",
                    "api: chip.set('flow','cts','script','/myrefdir/cts.tcl'"],
        'help' : """
        Path to the entry point compilation script called by the executable 
        specified on a per step basis.
        """
    }

    #copy
    cfg['flow'][step]['copy'] = {
        'switch' : '-flow_copy',
        'type' : ['bool'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Copy Local Option',
        'param_help' : "'flow' step 'copy' <bool>",
        'example': ["cli: -flow_copy cts ",
                    "api: chip.set('flow','cts','copy','true'"],
        'help' : """
        Specifies that the reference script directory should be copied and run 
        from the local run directory. The option specified on a per step basis.
        """
    }
    
    #script format
    cfg['flow'][step]['format'] = {
        'switch' : '-flow_format',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Script Format',
        'param_help' : "'flow' step 'format' <str>",
        'example': ["cli: -flow_format cts tcl ",
                    "api: chip.set('flow','cts','format','tcl'"],
        'help' : """
        Specifies that format of the configuration file for the step. Valid 
        formats are tcl, yaml, json, cmdline. The format used is dictated by 
        the executable for the step and specified on a per step basis.
        """
    }
    
    #parallelism
    cfg['flow'][step]['threads'] = {
        'switch' : '-flow_threads',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Job Parallelism',
        'param_help' : "'flow' step 'threads' <num>",
        'example': ["cli: -flow_threads drc 64 ",
                    "api: chip.set('flow','drc','threads','64'"],
        'help' : """
        Specifies the level of CPU thread parallelism to enable on a per step
        basis.
        """
    }
    
    #cache
    cfg['flow'][step]['cache'] = {
        'switch' : '-flow_cache',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],  
        'short_help' : 'Cache Directory Name',
        'param_help' : "'flow' step 'cache' <file>",
        'example': ["cli: -flow_cache syn /disk1/mycache ",
                    "api: chip.set('flow','syn','cache','/disk1/mycache'"],
        'help' : """
        "Specifies a writeable shared cache directory to be used for storage of 
        processed design and library data. The purpose of caching is to save 
        runtime and disk space in future runs.
        """
    }
    
    #warnings
    cfg['flow'][step]['warningoff'] = {
        'switch' : '-flow_warningoff',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Warning Filter',
        'param_help' : "'flow' step 'warningoff' <file>",
        'example': ["cli: -flow_warningoff import COMBDLY",
                    "api: chip.set('flow','import','warningoff','COMBDLY'"],
        'help' : """
        Specifies a list of EDA warnings for which printing should be supressed.
        Generally this is done on a per design/node bases after review has 
        determined that warning can be safely ignored
        """
    }
    
    #vendor
    cfg['flow'][step]['vendor'] = {
        'switch' : '-flow_vendor',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Step Vendor',
        'param_help' : "'flow' step 'vendor' <str>",
        'example': ["cli: -flow_vendor place openroad",
                    "api: chip.set('flow','place','vendor', 'openroad'"],
        'help' : """
        The vendor argument is used for selecting eda specific technology setup
        variables from the PDK and libraries which generally support multiple
        vendors for each implementation step
        """
    }

    return cfg

###########################################################################
# Metrics to Track 
###########################################################################

def schema_metrics(cfg, group, step='default'):

    if not group in cfg:
        cfg[group] = {}    

    cfg[group][step] = {}      # per step

    cfg[group][step]['cells'] = {
        'switch' : '-'+group+'_cells',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Total Cell Instances ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'cells' <num>",
        'example':["cli: -"+group+"_cells 'place 100'",
                   "api: chip.add('"+group+"','place','cells','100')"],
        'help' : """
        Metric tracking the total number of cells on a per step basis.
        In the case of FPGAs, the it represents the number of LUTs.
        """
    }    
    
    cfg[group][step]['area'] = {
        'switch' : '-'+group+'_area',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Cell Area ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'area' <num>",
        'example':["cli: -"+group+"_area 'place 100.00'",
                   "api: chip.add('"+group+"','place','area','100.00')"],
        'help' : """
        Metric tracking the total cell area on a per step basis
        specified in um^2.
        """
    }

    cfg[group][step]['density'] = {
        'switch' : '-'+group+'_density',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Cell Density ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'density' <num>",
        'example':["cli: -"+group+"_density 'place 99.9'",
                   "api: chip.add('"+group+"','place','density','99.9')"],
        'help' : """
        Metric tracking the density calculated as the ratio of cell area
        devided by the total core area available for placement. Value is
        specified as a percentage (%) and does not include filler cells.
        """
    }
    
    cfg[group][step]['power'] = {
        'switch' : '-'+group+'_power',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Active Power ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'power' <num>",
        'example':["cli: -"+group+"_power 'place 0.001'",
                   "api: chip.add('"+group+"','place','power','0.001')"],
        'help' : """       
        Metric tracking the worst case dynamic power of the design on a per 
        step basis calculated based on setup config and VCD stimulus.
        stimulus. Metric unit is Watts.
        """
    }    

    cfg[group][step]['leakage'] = {
        'switch' : '-'+group+'_leakage',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Leakage ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'leakage' <num>",
        'example':["cli: -"+group+"_leakage 'place 1e-6'",
                   "api: chip.add('"+group+"','place','leakage','1e-6')"],
        'help' : """
        Metric tracking the worst case leakage of the design on a per step 
        basis. Metric unit is Watts.
        """
    }

    cfg[group][step]['hold_tns'] = {
        'switch' : '-'+group+'_hold_tns',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Hold TNS ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'hold_tns' <num>",
        'example':["cli: -"+group+"_hold_tns 'place 0'",
                   "api: chip.add('"+group+"','place','hold_tns','0')"],
        'help' : """
        Metric tracking of total negative hold slack (TNS) on a per step basis.
        Metric unit is nanoseconds.
        """
    }    

    cfg[group][step]['hold_wns'] = {
        'switch' : '-'+group+'_hold_wns',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Hold WNS ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'hold_wns' <num>",
        'example':["cli: -"+group+"_hold_wns 'place 0'",
                   "api: chip.add('"+group+"','place','hold_wns','0')"],
        'help' :"""
        Metric tracking of worst negative hold slack (WNS) on a per step basis.
        Metric unit is nanoseconds.
        """
    }
    
    cfg[group][step]['setup_tns'] = {
        'switch' : '-'+group+'_setup_tns',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Setup TNS ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'setup_tns' <num>",
        'example':["cli: -"+group+"_setup_tns 'place 0'",
                   "api: chip.add('"+group+"','place','setup_tns','0')"],
        'help' : """
        Metric tracking of total negative setup slack (TNS) on a per step basis.
        Metric unit is nanoseconds.
        """
    }


    cfg[group][step]['setup_wns'] = {
        'switch' : '-'+group+'_setup_wns',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Setup WNS ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'setup_wns' <num>",
        'example':["cli: -"+group+"_setup_wns 'place 0'",
                   "api: chip.add('"+group+"','place','setup_wns','0')"],
        'help' : """
        Metric tracking of worst negative setup slack (WNS) on a per step basis.
        Metric unit is nanoseconds.
        """
    }

    cfg[group][step]['drv'] = {
        'switch' : '-'+group+'_drv',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Rule Violations ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'drv' <num>",
        'example':["cli: -"+group+"_drv 'dfm 0'",
                   "api: chip.add('"+group+"','dfm','drv','0')"],
        'help' : """
        Metric tracking the total number of design rule violations on per step
        basis.
        """
    }    
    
    cfg[group][step]['warnings'] = {
        'switch' : '-'+group+'_warnings',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Total Warnings ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'warnings' <num>",
        'example':["cli: -"+group+"_warnings 'dfm 0'",
                   "api: chip.add('"+group+"','dfm','warnings','0')"],
        
        'help' : """
        Metric tracking the total number of warnings on a per step basis.
        """
    }
    
    cfg[group][step]['errors'] = {
        'switch' : '-'+group+'_errors',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Total Errors ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'errors' <num>",
        'example':["cli: -"+group+"_errors 'dfm 0'",
                   "api: chip.add('"+group+"','dfm','errors','0')"],
        'help' : """
        Metric tracking the total number of errors on a per step basis.
        """
    }

    cfg[group][step]['runtime'] = {
        'switch' : '-'+group+'_runtime',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Total Runtime ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'runtime' <num>",
        'example':["cli: -"+group+"_runtime 'dfm 0:1:20'",
                   "api: chip.add('"+group+"','dfm','runtime','0:1:20')"],
        'help' : """
        Metric tracking the total runtime on a per step basis. Time recorded
        as wall clock time, with value expressed as hr:min:sec
        """
    }
    
    cfg[group][step]['memory'] = {
        'switch' : '-'+group+'_memory',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Total Memory ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'memory' <num>",
        'example':["cli: -"+group+"_memory 'dfm 10MB'",
                   "api: chip.add('"+group+"','dfm','memory','10MB')"],
        'help' : """
        Metric tracking the total memory on a per step basis. Value recorded
        as bytes, displayed with standard units: K,M,G,T,P,E for Kilo, Mega, 
        Giga, Tera, Peta, Exa (bytes).
        """
    }

    return cfg

###########################################################################
# Provenance Tracking
###########################################################################

def schema_provenance(cfg, group='provenance', step='default'):

    if not group in cfg:
        cfg[group] = {}    

    cfg[group][step] = {}      # per step
    
    cfg[group][step]['author'] = {
        'switch' : '-'+group+'_author',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Author ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'author' <str>",
        'example':["cli: -"+group+"_author 'dfm wcoyote'",
                   "api: chip.add('"+group+"','dfm','author','wcoyote')"],
        'help' : """ 
        Metric tracking the author on a per step basis.
        """
    }

    cfg[group][step]['userid'] = {
        'switch' : '-'+group+'_userid',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Date ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'userid' <str>",
        'example':["cli: -"+group+"_userid 'dfm 0982acea'",
                   "api: chip.add('"+group+"','dfm','userid','0982acea')"],
        'help' : """
        Metric tracking the run userid on a per step basis.
        """
    }

    cfg[group][step]['signature'] = {
        'switch' : '-'+group+'_signature',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Date ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'signature' <str>",
        'example':["cli: -"+group+"_signature 'dfm 473c04b'",
                   "api: chip.add('"+group+"','dfm','signature','473c04b')"],
        'help' : """
        Metric tracking the execution signature/hashid on a per step basis.
        """
    }

    cfg[group][step]['organization'] = {
        'switch' : '-'+group+'_organization',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Date ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'org' <str>",
        'example':["cli: -"+group+"_organization 'dfm earth'",
                   "api: chip.add('"+group+"','dfm','organization','earth')"],
        'help' : """
        Metric tracking the user's organization on a per step basis.
        """
    }

    cfg[group][step]['location'] = {
        'switch' : '-'+group+'_location',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Date ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'location' <str>",
        'example':["cli: -"+group+"_location 'dfm Boston'",
                   "api: chip.add('"+group+"','dfm','location','Boston')"],
        'help' : """
        Metric tracking the user's location on a per step basis.
        """
    }

    cfg[group][step]['date'] = {
        'switch' : '-'+group+'_date',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Date ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'date' <str>",
        'example':["cli: -"+group+"_date 'dfm 2021-05-01'",
                   "api: chip.add('"+group+"','dfm','date','2021-05-01')"],
        'help' : """
        Metric tracking the run date stamp on a per step basis.
        """
    }

    cfg[group][step]['time'] = {
        'switch' : '-'+group+'_time',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Date ' + group.capitalize(),
        'param_help' : "'"+group+"' step 'time' <str>",
        'example':["cli: -"+group+"_time 'dfm 11:35:40'",
                   "api: chip.add('"+group+"','dfm','time','11:35:40')"],
        'help' : """
        Metric tracking the run time stamp on a per step basis.
        """
    }

    return cfg


###########################################################################
# Run Options
###########################################################################

def schema_options(cfg):
    ''' Run-time options
    '''
    
    cfg['mode'] = {
        'switch' : '-mode',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : ['asic'],
        'short_help' : 'Compilation Mode',
        'param_help' : "'mode' <str>",
        'example': ["cli: -mode fpga",
                    "api: chip.set('mode','fpga'"],
        'help' : """
        Sets the compilation flow to 'fpga' or 'asic. The default is 'asic'
        """
    }

    cfg['target'] = {
        'switch' : '-target',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['custom'],
        'short_help' : 'Target Platform',
        'param_help' : "'target' <str>",
        'example': ["cli: -target freepdk45_openroad",
                    "api: chip.set('target','freepdk45_openroad'"],
        'help' : """
        Provides a string name for choosing a physical mapping target for the
        design. The target should be one of the following formats.

        1.) A single word target found in the targetmap list (freepdk45, asap7)
        2.) For ASICs, an underscore split string of format "process_edaflow"
        3.) For FPGAs, an underscore split string of format "device_edaflow"
        """
    }

    cfg['steplist'] = {
        'switch' : '-steplist',
        'requirement' : 'all',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'short_help' : 'Compilation Steps List',
        'param_help' : "'steplist' <str>",
        'example': ["cli: -steplist export",
                    "api: chip.add('steplist','export'"],
        'help' : """
        A complete list of all steps included in the compilation process.
        Compilation flow is controlled with the -start, -stop, -cont switches 
        and by adding values to the list. The list must be ordered to enable 
        default automated compilation from the first entry to the last entry 
        in the list. 
        """
    }

    cfg['cfg'] = {
        'switch' : '-cfg',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Configuration File',
        'param_help' : "'cfg' <file>",
        'example': ["cli: -cfg mypdk.json",
                    "api: chip.add('cfg','mypdk.json'"],
        'help' : """
        All parameters can be set at the command line, but with over 500 
        configuration parameters possible, the preferred method for non trivial
        use cases is to create a cfg file using the python API. The cfg file 
        can then be passed in through he -cfgfile switch at the command line.
        There  is no restriction on the number of cfg files that can be be 
        passed in. but it should be noted that the cfgfile are appended to the 
        existing list and configuration list.
        """
        }

    cfg['env'] = {}
    cfg['env']['default'] = {
        'switch' : '-env',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Environment Variables',
        'param_help' : "'env' varname <str>",
        'example': ["cli: -env 'PDK_HOME /disk/mypdk'",
                    "api: chip.add('env', 'PDK_HOME', '/disk/mypdk'"],
        'help' : """
        Certain EDA tools and reference flows require environment variables to
        be set. These variables can be managed externally or specified through
        the env variable.
        """
    }

    cfg['scpath'] = {
        'switch' : '-scpath',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Search path',
        'param_help' : "'scpath' <str>",
        'example': ["cli: -scpath '/home/$USER/sclib'",
                    "api: chip.add('scpath', '/home/$USER/sclib'"],
        'help' : """
        Specifies python modules paths for target import.
        """
    }

    cfg['hashmode'] = {
        'switch' : '-hashmode',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['NONE'],
        'short_help' : 'File Hash Mode',
        'param_help' : "'hashmode' <str>",
        'example': ["cli: -hashmode 'ALL'",
                    "api: chip.add('hasmode', 'ALL'"],
        'help' : """
        The switch controls how/if setup files and source files are hashed
        during compilation. Valid entries include NONE, ALL, USED.
        """
    }
    
    cfg['quiet'] = {
        'short_help' : 'Quiet Execution Option',
        'switch' : '-quiet',
        'type' : ['bool'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['false'],
        'short_help' : 'Quiet execution',
        'param_help' : "'quiet' <bool>",
        'example': ["cli: -quiet",
                    "api: chip.set('quiet', 'true'"],
        'help' : """
        Modern EDA tools print significant content to the screen. The -quiet 
        option forces all steps to print to a log file. The quiet
        option is ignored when the -noexit is set to true.
        """
    }

    cfg['loglevel'] = {
        'switch' : '-loglevel',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['WARNING'],
        'short_help' : 'Logging Level',
        'param_help' : "'loglevel' <str>",
        'example': ["cli: -loglevel INFO",
                    "api: chip.set('loglevel', 'INFO'"],
        'help' : """
        The debug param provides explicit control over the level of debug 
        logging printed. Valid entries include INFO, DEBUG, WARNING, ERROR. The
        default value is WARNING.
        """
    }

    cfg['dir'] = {
        'switch' : '-dir',
        'type' : ['dir'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['build'],
        'short_help' : 'Build Directory',
        'param_help' : "'dir' <dir>",
        'example': ["cli: -dir ./build_the_future",
                    "api: chip.set('dir','./build_the_future'"],
        'help' : """
        The default build directoryis './build'. The 'dir' parameters can be 
        used to set an alternate compilation directory path.
        """
    }
    
    cfg['jobname'] = {
        'switch' : '-jobname',
        'type' : ['dir'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Job Name',
        'param_help' : "'jobname' <dir>",
        'example': ["cli: -jobname may1",
                    "api: chip.set('jobname','may1'"],
        'help' : """
        By default, job directories are created inside the 'build' directory 
        in a sequential fashion as follows: job0, job1, job2,...
        The 'jobname' parameters allows user to manually specify a jobname.
        """
    }

    cfg['start'] = {
        'switch' : '-start',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Compilation Start Step',
        'param_help' : "'start' <str>",
        'example': ["cli: -start place",
                    "api: chip.set('start','place'"],
        'help' : """
        The start parameter specifies the starting step of the flow. This would
        generally be the import step but could be any one of the steps within
        the steps parameter. For example, if a previous job was stopped at syn a
        job can be continued from that point by specifying -start place
        """
    }

    cfg['stop'] = {
        'switch' : '-stop',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'requirement' : 'optional',
        'short_help' : 'Compilation Stop Step',
        'param_help' : "'stop' <str>",
        'example': ["cli: -stop place",
                    "api: chip.set('stop','place'"],
        'help' : """
        The stop parameter specifies the stopping step of the flow. The value
        entered is inclusive, so if for example the -stop syn is entered, the 
        flow stops after syn has been completed.
        """
    }

    cfg['skip'] = {
        'switch' : '-skip',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'requirement' : 'optional',
        'short_help' : 'Compilation Skip Steps',
        'param_help' : "'skip' <str>",
        'example': ["cli: -stop dfm",
                    "api: chip.set('stop','dfm'"],
        'help' : """
        In some older technologies it may be possible to skip some of the steps 
        in the standard flow defined. The skip parameter lists the steps to be 
        skipped during execution.
        """
    }

    cfg['skipall'] = {
        'switch' : '-skipall',
        'type' : ['bool'],
        'lock' : 'false',
        'defvalue' : ['false'],
        'requirement' : 'optional',
        'short_help' : 'Skip All Steps',
        'param_help' : "'skipall' <bool>",
        'example': ["cli: -skipall",
                    "api: chip.set('skipall','true'"],
        'help' : """
        Skip all steps. Useful for initial bringup.
        """
    }
    
    
    cfg['msgevent'] = {
        'switch' : '-msgevent',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Message Event',
        'param_help' : "'msgevent' <str>",
        'example': ["cli: -msgevent export",
                    "api: chip.set('msgevent','export'"],
        'help' : """
        A list of steps after which to notify a recipient. For example if 
        values of syn, place, cts are entered separate messages would be sent 
        after the completion of the syn, place, and cts steps.
        """
    }

    cfg['msgcontact'] = {
        'switch' : '-msgcontact',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Message Contact',
        'param_help' : "'msgcontact' <str>",
        'example': ["cli: -msgcontact 'wile.e.coyote@acme.com'",
                    "api: chip.set('msgcontact','wile.e.coyote@acme.com'"],
        'help' : """
        A list of phone numbers or email addresses to message on a event event
        within the msg_event param.
        """
    }

    cfg['optmode'] = {
        'switch' : '-O',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['O0'],
        'short_help' : 'Optimization Mode',
        'param_help' : "'optmode' <str>",
        'example': ["cli: -O3'",
                    "api: chip.set('optmode','3'"],
        'help' : """
        The compiler has modes to prioritize run time and ppa. Modes include:
        
        (0) = Exploration mode for debugging setup           
        (1) = Higher effort and better PPA than O0           
        (2) = Higher effort and better PPA than O1           
        (3) = Signoff qualtiy. Better PPA and higher run times than O2
        (4) = Experimental highest effort, may be unstable.   
        """
    }
    
    cfg['relax'] = {
        'switch' : '-relax',
        'type' : ['bool'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['false'],
        'short_help' : 'Relaxed RTL Linting',
        'param_help' : "'relax' <bool>",
        'example': ["cli: -relax'",
                    "api: chip.set('relax', 'true')"],
        'help' : """
        Specifies that tools should be lenient and supress some warnigns that 
        may or may not indicate design issues. The default is to enforce strict
        checks for all steps.
        """
    }

    cfg['clean'] = {
        'switch' : '-clean',
        'type' : ['bool'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['false'],
        'short_help' : 'Keep essential files only',
        'param_help' : "'clean' <bool>",
        'example': ["cli: -clean'",
                    "api: chip.set('clean', 'true')"],
        'help' : """
        Deletes all non-essential files at the end of each step and creates a 
        'zip' archive of the job folder.
        """
    }
    
    cfg['bkpt'] = {
        'switch' : '-bkpt',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : ['false'],
        'short_help' : "A list of flow breakpoints",
        'param_help' : "'bkpt' <str>",
        'example': ["cli: -bkpt place",
                    "api: chip.add('bkpt', 'place')"],
        'help' : """
        Specifies a list of step stop (break) points. If the step is
        a TCL based tool, then the breakpoints stops the flow inside the EDA
        tool. If the step is a command line tool, then the flow drops into
        a Python interpreter.
        """
    }

    # Remote IP address/host name running sc-server app
    cfg['remote'] = {
        'switch': '-remote',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Remote Server Address',
        'param_help' : "'remote' <str>",
        'example': ["cli: -remote 192.168.1.100",
                    "api: chip.add('remote', '192.168.1.100')"],
        'help' : """
        Dicates that all steps after the compilation step should be executed
        on the remote server specified by the IP address. 
        """
    }
    
    # Port number that the remote host is running 'sc-server' on.
    cfg['remoteport'] = {
        'switch': '-remoteport',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'remote',
        'defvalue' : ['8080'],
        'short_help': 'Remove Server Port',
        'param_help' : "'remoteport' <str>",
        'example': ["cli: -remoteport 8080",
                    "api: chip.add('remoteport', '8080')"],
        'help' : """
        Sets the server port to be used in communicating with the remote host.
        """
    }

    # Path to a config file defining multiple remote jobs to run.
    cfg['permutations'] = {
        'switch' : '-permutations',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : "Run Permutations File",
        'param_help' : "'permutations' <file>",
        'example': ["cli: -permutations permute.py",
                    "api: chip.add('permuations', 'permute.py')"],
        'help' : """
        Sets the path to a Python file containing a generator which yields
        multiple configurations of a job to run in parallel. This lets you
        sweep various configurations such as die size or clock speed.
        """
    }

    return cfg


############################################
# Runtime status
#############################################

def schema_status(cfg):

    cfg['status'] ={}
    cfg['status']['step'] = {
        'switch' : '-status_step',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Current Compilation Step',
        'param_help' : "'status' 'step' <str>",
        'example': ["api: chip.get('status', 'step')"],
        'help' : """
        A dynamic variable that keeps track of the current name being executed.
        The variable is managed by the run function and not writable by the 
        user.
        """
    }

    cfg['status']['default'] = { }
    cfg['status']['default']['active'] = {
        'switch' : '-status_active',
        'type' : ['bool'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Step Active Indicator',
        'param_help' : "'status' step 'active' <bool>",
        'example': ["api: chip.get('status', 'step', 'active')"],
        'help' : """
        Status field with boolean indicating step activity. The variable is 
        managed by the run function and not writable by the user.
        true=active/processing, false=inactive/done
        """
        }
        
    return cfg

############################################
# Design Setup
#############################################

def schema_design(cfg):
    ''' Design Sources
    '''

    cfg['source'] = {
        'switch' : 'None',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Design Source Files',
        'param_help' : "'source' <file>",
        'example': ["cli: hello_world.v",
                    "api: chip.add('source', 'hello_world.v')"],
        'help' : """
        A list of source files to read in for elaboration. The files are read 
        in order from first to last entered. File type is inferred from the 
        file suffix:

        (*.v, *.vh) = Verilog
        (*.sv)      = SystemVerilog
        (*.vhd)     = VHDL
        """
    }

    cfg['doc'] = {
        'switch' : '-doc',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Design Documentation',
        'param_help' : "'doc' <file>",
        'example': ["cli: -doc spec.pdf",
                    "api: chip.add('doc', 'spec.pdf')"],
        'help' : """
        A list of design documents. Files are read in order from first to last.
        """
    }

    cfg['rev'] = {
        'switch' : '-rev',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Design Revision',
        'param_help' : "'rev' <str>",
        'example': ["cli: -rev 1.0",
                    "api: chip.add('rev', '1.0')"],
        'help' : """
        Specifies the revision of the current design.
        """
    }

    cfg['license'] = {
        'switch' : '-license',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'all',
        'defvalue' : [],
        'short_help' : 'Design License File',
        'param_help' : "'license' <file>",
        'example': ["cli: -license ./LICENSE",
                    "api: chip.add('license', './LICENSE')"],
        'help' : """
        Filepath to the technology license for currrent design.
        """
    }
  
    cfg['design'] = {
        'switch' : '-design',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Top Module Name',
        'param_help' : "'design' <str>",
        'example': ["cli: -design hello_world",
                    "api: chip.add('design', 'hello_world')"],
        'help' : """
        Name of the top level design to compile. Required for all designs with
        more than one module.
        """
    }

    cfg['nickname'] = {
        'switch' : '-nickname',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Nickname',
        'param_help' : "'nickname' <str>",
        'example': ["cli: -nickname hello",
                    "api: chip.add('nickname', 'hello')"],
        'help' : """
        An alias for the top level design name. Can be useful when top level 
        designs have long and confusing names. The nickname is used in all 
        output file prefixes.
        """
    }

    cfg['origin'] = {
        'switch' : '-origin',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Origin',
        'param_help' : "'origin' <str>",
        'example': ["cli: -origin mars",
                    "api: chip.add('origin', 'mars')"],
        'help' : """
        Record of design source origin.
        """
    }

    cfg['clock'] = {}
    cfg['clock']['default'] = {}
    
    cfg['clock']['default']['pin'] = {
        'switch' : '-clock_name',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Clock Driver',
        'param_help' : "'clock' clkname 'pin' <str>",
        'example': ["cli: -clock_pin 'clk top.pll.clkout'",
                    "api: chip.add('clock', 'clk','pin','top.pll.clkout')"],
        'help' : """
        Defines a clock name alias to assign to a clock source.
        """
    }
    
    cfg['clock'] = {}
    cfg['clock']['default'] = {}
    cfg['clock']['default']['period'] = {
        'switch' : '-clock_period',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Clock Period',
        'param_help' : "'clock' clkname 'period' <num>",
        'example': ["cli: -clock_period 'clk 10'",
                    "api: chip.add('clock','clk','period','10')"],
        'help' : """
        Specifies the period for a clock source in nanoseconds.
        """
    }
    
    cfg['clock']['default']['jitter'] = {
        'switch' : '-clock_jitter',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Clock Jitter',
        'param_help' : "'clock' clkname 'jitter' <num>",
        'example': ["cli: -clock_jitter 'clk 0.01'",
                    "api: chip.add('clock','clk','jitter','0.01')"],
        'help' : """
        Specifies the jitter for a clock source in nanoseconds.
        """
    }

    cfg['supply'] = {}
    cfg['supply']['default'] = {}
            
    cfg['supply']['default']['pin'] = {
        'switch' : '-supply_name',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Power Supply Name',
        'param_help' : "'supply' supplname 'pin' <str>",
        'example': ["cli: -supply_pin 'vdd vdd_0'",
                    "api: chip.add('supply','vdd','pin','vdd_0')"],
        'help' : """
        Defines a supply name alias to assign to a power source.
        A power supply source can be a list of block pins or a regulator
        output pin.

        Examples:
        cli: -supply_name 'vdd_0 vdd'
        api: chip.add('supply','vdd_0', 'name', 'vdd')
        """
    }

    cfg['supply']['default']['level'] = {
        'switch' : '-supply_level',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Power Supply Level',
        'param_help' : "'supply' supplyname 'level' <num>",
        'example': ["cli: -supply_level 'vdd 1.0'",
                    "api: chip.add('supply','vdd','level','1.0')"],
        'help' : """
        Specifies level in Volts for a power source.
        """
    }

    cfg['supply']['default']['noise'] = {
        'switch' : '-supply_noise',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Power Supply Noise',
        'param_help' : "'supply' supplyname 'noise' <num>",
        'example': ["cli: -supply_noise 'vdd 0.05'",
                    "api: chip.add('supply','vdd','noise','0.05')"],
        'help' : """
        Specifies the noise in Volts for a power source.
        """
    }
  
    cfg['define'] = {
        'switch' : '-D',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Design Preprocessor Symbols',
        'param_help' : "'define' <str>",
        'example': ["cli: -D 'CFG_ASIC=1'",
                    "api: chip.add('define','CFG_ASIC=1')"],
        'help' : """
        Sets a preprocessor symbol for verilog source imports.
        """
    }

    cfg['ydir'] = {
        'switch' : '-y',
        'type' : ['dir'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Design Module Search Paths',
        'param_help' : "'ydir' <dir>",
        'example': ["cli: -y './mylib'",
                    "api: chip.add('ydir','./mylib')"],
        'help' : """
        Provides a search paths to look for modules found in the the source 
        list. The import engine will look for modules inside files with the 
        specified +libext+ param suffix
        """
    }

    cfg['idir'] = {
        'switch' : '-I',
        'type' : ['dir'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Design Include Search Paths',
        'param_help' : "'idir' <dir>",
        'example': ["cli: -I'./mylib'",
                    "api: chip.add('idir','./mylib')"],
        'help' : """
        Provides a search paths to look for files included in the design using
        the `include statement.
        """
    }

    cfg['vlib'] = {
        'switch' : '-v',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Verilog Library',
        'param_help' : "'vlib' <file>",
        'example': ["cli: -v './mylib.v'",
                    "api: chip.add('vlib','./mylib.v')"],
        'help' : """
        Declares source files to be read in, for which modules are not to be 
        interpreted as root modules.
        """
    }

    cfg['libext'] = {
        'switch' : '+libext',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'short_help' : 'Verilog File Extensions',
        'param_help' : "'libext' <str>",
        'example': ["cli:  +libext+sv'",
                    "api: chip.add('libext','sv')"],
        'help' : """
        Specifes the file extensions that should be used for finding modules. 
        For example, if -y is specified as ./lib", and '.v' is specified as 
        libext then the files ./lib/*.v ", will be searched for module matches.
        """
    }

    cfg['cmdfile'] = {
        'switch' : '-f',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Verilog Options File',
        'param_help' : "'cmdfile' <file>",
        'example': ["cli: -f design.f",
                    "api: chip.add('cmdfile','design.f')"],
        'help' : """
        Read the specified file, and act as if all text inside it was specified
        as command line parameters. Supported by most verilog simulators 
        including Icarus and Verilator.
        """
    }

    cfg['constraint'] = {
        'switch' : '-constraint',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Design Constraint Files',
        'param_help' : "'constraint' <file>",
        'example': ["cli: -constraint top.sdc",
                    "api: chip.add('constraint','top.sdc')"],
        'help' : """
        List of default constraints for the design to use during compilation. 
        Types of constraints include timing (SDC) and pin mappings for FPGAs.
        More than one file can be supplied. Timing constraints are global and 
        sourced in all MCMM scenarios.
        """
    }

    cfg['vcd'] = {
        'switch' : '-vcd',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Value Change Dump File',
        'param_help' : "'vcd' <file>",
        'example': ["cli: -vcd mytrace.vcd",
                    "api: chip.add('vcd','mytrace.vcd')"],
        'help' : """
        A digital simulation trace that can be used to model the peak and 
        average power consumption of a design.
        """
    }

    cfg['spef'] = {
        'switch' : '-spef',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'SPEF File',
        'param_help' : "'spef' <file>",
        'example': ["cli: -spef mydesign.spef",
                    "api: chip.add('spef','mydesign.spef')"],
        'help' : """
        File containing parastics specified in the Standard Parasitic Exchange
        format. The file is used in signoff static timing analysis and power
        analysis and should be generated by an accurate parasitic extraction
        engine.
        """
    }

    cfg['sdf'] = {
        'switch' : '-sdf',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'SDF File',
        'param_help' : "'sdf' <file>",
        'example': ["cli: -sdf mydesign.sdf",
                    "api: chip.add('sdf','mydesign.sdf')"],
        'help' : """
        File containing timing data in Standard Delay Format (SDF).
        """
    }
    
    return cfg

###########################
# ASIC Setup
###########################

def schema_asic(cfg):
    ''' ASIC Automated Place and Route Parameters
    '''

    cfg['asic'] = {}
    
    cfg['asic']['targetlib'] = {
        'switch' : '-asic_targetlib',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'requirement' : 'asic',
        'short_help' : 'Target Libraries',
        'param_help' : "'asic' 'targetlib' <str>",
        'example': ["cli: -asic_targetlib asap7sc7p5t_lvt",
                    "api: chip.add('asic', 'targetlib', 'asap7sc7p5t_lvt')"],
        'help' : """
        A list of library names to use for synthesis and automated place and 
        route. Names must match up exactly with the library name handle in the 
        'stdcells' dictionary.
        """
    }

    cfg['asic']['macrolib'] = {
        'switch' : '-asic_macrolib',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'requirement' : 'optional',
        'short_help' : 'Macro Libraries',
        'param_help' : "'asic' 'macrolib' <str>",
        'example': ["cli: -asic_macrolib sram64x1024",
                    "api: chip.add('asic', 'macrolib', 'sram64x1024')"],
        'help' : """
        A list of macro libraries to be linked in during synthesis and place
        and route. Macro libraries are used for resolving instances but are 
        not used as target for automated synthesis.
        """
    }
        
    cfg['asic']['delaymodel'] = {
        'switch' : '-asic_delaymodel',
        'type' : ['str'],
        'lock' : 'false',
        'defvalue' : [],
        'requirement' : 'asic',
        'short_help' : 'Library Delay Model',
        'param_help' : "'asic' 'delaymodel' <str>",
        'example': ["cli: -asic_delaymodel ccs",
                    "api: chip.add('asic', 'delaymodel', 'ccs')"],
        'help' : """
        Specifies the delay model to use for the target libs. Supported values
        are nldm and ccs.
        """
    }
    
    cfg['asic']['ndr'] = {
        'switch' : '-asic_ndr',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : '',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Design Non-default Rules',
        'param_help' : "'asic' 'ndr' <str>",
        'example': ["cli: -asic_ndr myndr.txt",
                    "api: chip.add('asic', 'ndr', 'myndr.txt')"],
        'help' : """
        A file containing a list of nets with non-default width and spacing,
        with one net per line and no wildcards. 
        The file format is: <netname width space>. The netname should include 
        the full hierarchy from the root module while width space should be 
        specified in the resolution specified in the technology file.
        The values are specified in microns.
        """
    }

    cfg['asic']['minlayer'] = {
        'switch' : '-asic_minlayer',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'Design Minimum Routing Layer',
        'param_help' : "'asic' 'minlayer' <str>",
        'example': ["cli: -asic_minlayer m2",
                    "api: chip.add('asic', 'minlayer', 'm2')"],
        'help' : """
        The minimum layer to be used for automated place and route. The layer 
        can be supplied as an integer with 1 specifying the first routing layer
        in the apr_techfile. Alternatively the layer can be a string that 
        matches a layer hardcoded in the pdk_aprtech file. Designers wishing to
        use the same setup across multiple process nodes should use the integer
        approach. For processes with ambigous starting routing layers, exact 
        strings should be used.
        """
    }

    cfg['asic']['maxlayer'] = {
        'switch' : '-maxlayer',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'Design Maximum Routing Layer',
        'param_help' : "'asic' 'maxlayer' <str>",
        'example': ["cli: -asic_maxlayer m6",
                    "api: chip.add('asic', 'maxlayer', 'm6')"],
        'help' : """
        The maximum layer to be used for automated place and route. The layer 
        can be supplied as an integer with 1 specifying the first routing layer
        in the apr_techfile. Alternatively the layer can be a string that 
        matches a layer hardcoded in the pdk_aprtech file. Designers wishing to
        use the same setup across multiple process nodes should use the integer
        approach. For processes with ambigous starting routing layers, exact 
        strings should be used.
        """
    }

    cfg['asic']['stackup'] = {
        'switch' : '-asic_stackup',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'Design Metal Stackup',
        'param_help' : "'asic' 'stackup' <str>",
        'example': ["cli: -asic_stackup 2MA4MB2MC",
                    "api: chip.add('asic','stackup','2MA4MB2MC')"],
        'help' : """
        Specifies the target stackup to use in the design. The stackup name 
        must match a value defined in the pdk_stackup list.
        """
    }
    
    # For density driven floorplanning
    cfg['asic']['density'] = {
        'switch' : '-asic_density',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : '!diesize',
        'defvalue' : [],
        'short_help' : 'APR Target Core Density',
        'param_help' : "'asic' 'density' <num>",
        'example': ["cli: -asic_density 30",
                    "api: chip.add('asic', 'density', '30')"],
        'help' : """"
        Provides a target density based on the total design cell area reported
        after synthesis. This number is used when no die size or floorplan is 
        supplied. Any number between 1 and 100 is legal, but values above 50 
        may fail due to area/congestion issues during apr.
        """
    }

    cfg['asic']['coremargin'] = {
        'switch' : '-asic_coremargin',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'density',
        'defvalue' : [],
        'short_help' : 'APR Block Core Margin',
        'param_help' : "'asic' 'coremargin' <num>",
        'example': ["cli: -asic_coremargin 1",
                    "api: chip.add('asic', 'coremargin', '1')"],
        'help' : """
        Sets the halo/margin between the core area to use for automated 
        floorplanning and the outer core boundary. The value is specified in 
        microns and is only used when no diesize or floorplan is supplied.
        """
    }

    cfg['asic']['aspectratio'] = {
        'switch' : '-asic_aspectratio',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'density',
        'defvalue' : ['1'],
        'short_help' : 'APR Block Aspect Ratio',
        'param_help' : "'asic' 'aspectratio' <num>",
        'example': ["cli: -asic_aspectratio 2.0",
                    "api: chip.add('asic', 'aspectratio', '2.0')"],
        'help' : """
        Specifies the height to width ratio of the block for  automated 
        floor-planning. Values below 0.1 and above 10 should be avoided as 
        they will likely fail to converge during placement and routing. The 
        ideal aspect ratio for most designs is 1.
        """
        }

    # For spec driven floorplanning
    cfg['asic']['diesize'] = {
        'switch' : '-asic_diesize',
        'type' : ['num', 'num', 'num', 'num'],
        'lock' : 'false',
        'requirement' : '!density',
        'defvalue' : [],
        'short_help' : 'Target Die Size',
        'param_help' : "'asic' 'diesize' <num num num num>",
        'example': ["cli: -asic_diesize '0 0 100 100'",
                    "api: chip.add('asic', 'diesize', '0 0 100 100')"],
        'help' : """
        Provides the outer boundary of the physical design. The number is 
        provided as a tuple (x0 y0 x1 y1), where (x0, y0), specifes the lower 
        left corner of the block and (x1, y1) specifies the upper right corner.
        Only rectangular blocks are supported with the diesize parameter. All
        values are specified in microns.
        """
    }
    
    cfg['asic']['coresize'] = {
        'switch' : '-asic_coresize',
        'type' : ['num', 'num', 'num', 'num'],
        'lock' : 'false',
        'requirement' : 'diesize',
        'defvalue' : [],
        'short_help' : 'Target Core Size',
        'param_help' : "'asic' 'coresize' <num num num num>",
        'example': ["cli: -asic_coresize '0 0 90 90'",
                    "api: chip.add('asic', 'coresize', '0 0 90 90')"],
        'help' : """
        Provides the core cell area of the physical design. The number is 
        provided as a tuple (x0 y0 x1 y1), where (x0, y0), specifes the lower 
        left corner of the block and (x1, y1) specifies the upper right corner.
        Only rectangular blocks are supported with the diesize parameter. For
        advanced geometries and blockages, a floor-plan file should is better.
        All values are specified in microns.
        """
    }

    # Parameterized floorplanning
    cfg['asic']['floorplan'] = {
        'switch' : '-asic_floorplan',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Floorplanning Script',
        'param_help' : "'asic' 'floorplan' <file>",
        'example': ["cli: -asic_floorplan 'hello.py'",
                    "api: chip.add('asic', 'floorplan', 'hello.py')"],
        'help' : """
        Provides a parameterized floorplan to be used during the floorplan step
        of compilation to generate a fixed DEF ready for use by the APR tool.
        Supported formats are tcl and py.
        """
    }

    # Def file
    cfg['asic']['def'] = {
        'switch' : '-asic_def',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'optional',
        'defvalue' : [],
        'hash'   : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'short_help' : 'Harc coded DEF floorplan',
        'param_help' : "'asic' 'def' <file>",
        'example': ["cli: -asic_def 'hello.def'",
                    "api: chip.add('asic', 'def', 'hello.def')"],
        'help' : """
        Provides a hard coded DEF floorplan to be used during the floorplan step
        and/or initial placement step.
        """
    }

    return cfg

############################################
# Constraints
############################################

def schema_mcmm(cfg):

    cfg['mcmm'] = {}
    cfg['mcmm']['default'] = {}

    cfg['mcmm']['default']['voltage'] = {
        'switch' : '-mcmm_voltage',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM Voltage',
        'param_help' : "'mcmm' scenario 'voltage' <num>",
        'example': ["cli: -mcmm_voltage 'worst 0.9'",
                    "api: chip.add('mcmm', 'worst', 'voltage', '0.9'"],
        'help' : """
        Specifies the on chip primary core operating voltage for the scenario.
        The value is specified in Volts.
        """
    }

    cfg['mcmm']['default']['temperature'] = {
        'switch' : '-mcmm_temperature',
        'type' : ['num'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM Temperature',
        'param_help' : "'mcmm' scenario 'temperature' <num>",
        'example': ["cli: -mcmm_temperature 'worst 0.9'",
                    "api: chip.add('mcmm', 'worst', 'temperature', '125'"],
        'help' : """
        Specifies the on chip temperature for the scenario. The value is specified in 
        degrees Celsius.
        """
    }
    
    cfg['mcmm']['default']['libcorner'] = {
        'switch' : '-mcmm_libcorner',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM Library Corner Name',
        'param_help' : "'mcmm' scenario 'libcorner' <str>",
        'example': ["cli: -mcmm_libcorner 'worst ttt'",
                    "api: chip.add('mcmm', 'worst', 'libcorner', 'ttt'"],
        'help' : """
        Specifies the library corner for the scenario. The value is used to access the
        stdcells library timing model. The 'libcorner' value must match the corner 
        in the 'stdcells' dictionary exactly. 
        """
    }

    cfg['mcmm']['default']['opcond'] = {
        'switch' : '-mcmm_opcond',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM Operating Condition',
        'param_help' : "'mcmm' scenario 'opcond' <str>",
        'example': ["cli: -mcmm_opcond 'worst typical_1.0'",
                    "api: chip.add('mcmm', 'worst', 'opcond', 'typical_1.0'"],
        'help' : """
        Specifies the operating condition for the scenario. The value can be used
        to access specific conditions within the library timing models of the 
        'target_libs'. The 'opcond' value must match the corner in the 
        timing model.
        """
    }
    
    cfg['mcmm']['default']['pexcorner'] = {
        'switch' : '-mcmm_pexcorner',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM PEX Corner Name',
        'param_help' : "'mcmm' scenario 'pexcorner' <str>",
        'example': ["cli: -mcmm_pexcorner 'worst max'",
                    "api: chip.add('mcmm', 'worst', 'pexcorner', 'max'"],
        'help' : """
        Specifies the parasitic corner for the scenario. The 'pexcorner' string must
        match the value 'pdk','pexmodel' dictionary exactly.
        """
    }

    cfg['mcmm']['default']['mode'] = {
        'switch' : '-mcmm_mode',
        'type' : ['str'],
        'lock' : 'false',
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM Mode Name',
        'param_help' : "'mcmm' scenario 'mode' <str>",
        'example': ["cli: -mcmm_mode 'worst test'",
                    "api: chip.add('mcmm', 'worst', 'mode', 'test'"],
        'help' : """
        Specifies the operating mode for the scenario. Operating mode strings can be
        values such as "test, functional, standby".
        """
    }

    cfg['mcmm']['default']['constraint'] = {
        'switch' : '-mcmm_constraint',
        'type' : ['file'],
        'lock' : 'false',
        'requirement' : 'asic',
        'hash' : [],
        'date'   : [],
        'author' : [],
        'signature' : [],
        'defvalue' : [],
        'short_help' : 'MCMM Timing Constraints',
        'param_help' : "'mcmm' scenario 'constraint' <str>",
        'example': ["cli: -mcmm_constraint 'worst hello.sdc'",
                    "api: chip.add('mcmm', 'worst', 'constraint', 'hello.sdc'"],
        'help' : """
        Specifies a list of timing contstraint files to use for the scenario.
        The values are combined with any constraints specified by the design
        'constraint' parameter. If no constraints are found, a default constraint
        file is used based on the clock definitions.
        """
    }

    cfg['mcmm']['default']['check'] = {
        'switch' : '-mcmm_check',
        'type' : ['str'],
        'lock' : 'false',        
        'requirement' : 'asic',
        'defvalue' : [],
        'short_help' : 'MCMM Checks',
        'param_help' : "'mcmm' scenario 'check' <str>",
        'example': ["cli: -mcmm_check 'worst check setup'",
                    "api: chip.add('mcmm', 'worst', 'check', 'setup'"],
        'help' : """
        Specifies a list of checks for to perform for the scenario aligned. The checks
        must align with the capabilities of the EDA tools. Checks generally include 
        objectives like meeting setup and hold goals and minimize power. 
        Standard check names include setup, hold, power, noise, reliability.
        """
    }

    return cfg

###############################################
# LEF/DEF
###############################################

def schema_lef(layout):

    #GLOBAL VARIABLES
    layout["version"] = ""
    layout["busbitchars"] = "[]"
    layout["dividerchar"] = "/"
    layout["units"] = ""
    layout["manufacturinggrid"] = ""

    #SITE
    layout["site"] = {}
    layout["site"]['default'] = {
        'symmetry' : "",
        'class' : "",
        'width' : "",
        'height' : ""
    }
    
    #ROUTING LAYERS
    layout["layer"] = {}
    layout["layer"]['default'] = {
        'number' : "",
        'direction' : "",
        'type' : "",
        'width' : "",
        'pitch' : "",
        'spacing' : "",
        'minwidth' : "",
        'maxwidth' : "",
        'antennaarearatio' : "",
        'antennadiffarearatio'  : ""
    }

    #MACROS
    layout["macro"] = {}
    layout["macro"]['default'] = {
        'class' : "",
        'site' : "",
        'width' : "",
        'height' : "",
        'origin' : "",
        'symmetry' : ""
    }
    layout["macro"]['default']['pin'] = {}
    layout["macro"]['default']['pin']['default'] = {
        'direction' : '',
        'use' : '',
        'shape' : '',
        'port' : []
    }


    return layout

def schema_def(layout):

    #DESIGN
    layout["design"] = []
    
    #DIEAREA
    #Arrray of points, kept as tuple arrray b/c order
    #is critical    
    layout["diearea"] = []
    
    #ROWS
    layout["row"] = {}    
    layout["row"]['default'] = {
        'site' : "",
        'x' : "",
        'y' : "",
        'orientation' : "",
        'numx' : "",
        'numy' : "",
        'stepx' : "",
        'stepy' : ""
    }

    #TRACKS (hidden name)
    layout["track"] = {}
    layout["track"]['default'] = {
        'layer' : "",
        'direction' : "",
        'start' : "",
        'step' : "",
        'total' : ""
    }

    #COMPONENTS (instance name driven)
    layout["component"] ={}
    layout["component"]['default'] = {
        'cell' : "",
        'x' : "",
        'y' : "",
        'status' : "",
        'orientation' : "",
        'halo' : ""
    }

    #VIA
    layout["via"] = {}
    layout["via"]['default'] = {
        'net' : "",
        'special' : "",
        'placement' : "",
        'direction' : "",
        'port' : []
    }

    
    #PINS
    layout["pin"] = {}
    layout["pin"]['default'] = {
        'net' : "",
        'direction' : "",
        'use' : "",
    }
    layout["pin"]['default']['port'] = {}
    layout["pin"]['default']['port']['default'] = {
        'layer' : "",
        'box' : [],
        'status' : "",
        'point' : "",
        'orientation' : "",
     }
    

    #SPECIALNETS
    layout["specialnet"] = {}
    layout["specialnet"]['default'] = {
        'connections' : [],
        'shield' : [],
        'use' : "",
        'fixed' : [],
        'routed' : []
    }

    #NETS
    layout["net"] = {}
    layout["net"]['default'] = {
        'shield' : [],
        'use' : "",
        'fixed' : [],
        'routed' : []
    }
   
    return layout
