import os
import re
import shutil
import math
import siliconcompiler
from siliconcompiler.floorplan import _infer_diearea

####################################################################
# Make Docs
####################################################################

def make_docs():
    '''
    OpenROAD is an automated physical design platform for
    integrated circuit design with a complete set of features
    needed to translate a synthesized netlist to a tapeout ready
    GDSII.

    Documentation:https://github.com/The-OpenROAD-Project/OpenROAD

    Sources: https://github.com/The-OpenROAD-Project/OpenROAD

    Installation: https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts

    '''

    chip = siliconcompiler.Chip('<design>')
    chip.set('arg', 'step', '<step>')
    chip.set('arg', 'index', '<index>')
    # TODO: how to make it clear in docs that certain settings are
    # target-dependent?
    chip.load_target('freepdk45_demo')
    setup(chip)

    return chip

################################
# Setup Tool (pre executable)
################################

def setup(chip, mode='batch'):

    # default tool settings, note, not additive!

    tool = 'openroad'
    refdir = 'tools/'+tool
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    flow = chip.get('option', 'flow')
    pdkname = chip.get('option', 'pdk')

    if mode == 'show':
        clobber = True
        option = "-no_init -gui"
    else:
        clobber = False
        option = "-no_init"

    script = 'sc_apr.tcl'

    # exit automatically in batch mode and not bkpt
    if (mode=='batch') and (step not in chip.get('option', 'bkpt')):
        option += " -exit"

    chip.set('tool', tool, 'exe', tool, clobber=clobber)
    chip.set('tool', tool, 'vswitch', '-version', clobber=clobber)
    chip.set('tool', tool, 'version', '>=v2.0-3394', clobber=clobber)
    chip.set('tool', tool, 'format', 'tcl', clobber=clobber)
    chip.set('tool', tool, 'option',  step, index, option, clobber=clobber)
    chip.set('tool', tool, 'refdir',  step, index, refdir, clobber=clobber)
    chip.set('tool', tool, 'script',  step, index, script, clobber=clobber)

    # normalizing thread count based on parallelism and local
    threads = os.cpu_count()
    if not chip.get('option', 'remote') and step in chip.getkeys('flowgraph', flow):
        np = len(chip.getkeys('flowgraph', flow, step))
        threads = int(math.ceil(os.cpu_count()/np))

    chip.set('tool', tool, 'threads', step, index, threads, clobber=clobber)

    # Input/Output requirements
    if step == 'floorplan':
        if (not chip.valid('input', 'netlist') or
            not chip.get('input', 'netlist')):
            chip.add('tool', tool, 'input', step, index, chip.design +'.vg')
    else:
        if (not chip.valid('input', 'def') or
            not chip.get('input', 'def')):
            chip.add('tool', tool, 'input', step, index, chip.design +'.def')

    chip.add('tool', tool, 'output', step, index, chip.design + '.sdc')
    chip.add('tool', tool, 'output', step, index, chip.design + '.vg')
    chip.add('tool', tool, 'output', step, index, chip.design + '.def')

    # openroad makes use of these parameters
    targetlibs = chip.get('asic', 'logiclib')
    stackup = chip.get('asic', 'stackup')
    if stackup and targetlibs:
        mainlib = targetlibs[0]
        macrolibs = chip.get('asic', 'macrolib')
        #Note: only one footprint supported in maainlib
        libtype = chip.get('library', mainlib, 'asic', 'libarch')

        chip.add('tool', tool, 'require', step, index, ",".join(['asic', 'logiclib']))
        chip.add('tool', tool, 'require', step, index, ",".join(['asic', 'stackup',]))
        # chip.add('tool', tool, 'require', step, index, ",".join(['library', mainlib, 'asic', 'footprint', libtype, 'symmetry']))
        # chip.add('tool', tool, 'require', step, index, ",".join(['library', mainlib, 'asic', 'footprint', libtype, 'size']))
        chip.add('tool', tool, 'require', step, index, ",".join(['pdk', pdkname, 'aprtech', 'openroad', stackup, libtype, 'lef']))
        if chip.valid('input', 'floorplan.def'):
            chip.set('tool', tool, 'require', step, index, ",".join(['input', 'floorplan.def']))

        for lib in (targetlibs + macrolibs):
            if 'nldm' in chip.getkeys('library', lib, 'model', 'timing'):
                for corner in chip.getkeys('library', lib, 'model', 'timing', 'nldm'):
                    chip.add('tool', tool, 'require', step, index, ",".join(['library', lib, 'model', 'timing', 'nldm', corner]))
            chip.add('tool', tool, 'require', step, index, ",".join(['library', lib, 'model', 'layout', 'lef', stackup]))
    else:
        chip.error = 1
        chip.logger.error(f'Stackup and logiclib parameters required for OpenROAD.')

    variables = (
        'place_density',
        'pad_global_place',
        'pad_detail_place',
        'macro_place_halo',
        'macro_place_channel'
    )
    for variable in variables:
        # For each OpenROAD tool variable, read default from PDK and write it
        # into schema. If PDK doesn't contain a default, the value must be set
        # by the user, so we add the variable keypath as a requirement.
        if chip.valid('pdk', pdkname, 'var', tool, stackup, variable):
            value = chip.get('pdk', pdkname, 'var', tool, stackup, variable)
            # Clobber needs to be False here, since a user might want to
            # overwrite these.
            chip.set('tool', tool, 'var', step, index, variable, value,
                     clobber=False)

        keypath = ','.join(['tool', tool, 'var', step, index, variable])
        chip.add('tool', tool, 'require', step, index, keypath)

    #for clock in chip.getkeys('clock'):
    #    chip.add('tool', tool, 'require', step, index, ','.join(['clock', clock, 'period']))
    #    chip.add('tool', tool, 'require', step, index, ','.join(['clock', clock, 'pin']))

    #for supply in chip.getkeys('supply'):
    #    chip.add('tool', tool, 'require', step, index, ','.join(['supply', supply, 'level']))
    #    chip.add('tool', tool, 'require', step, index, ','.join(['supply', supply, 'pin']))

    # basic warning and error grep check on logfile
    chip.set('tool', tool, 'regex', step, index, 'warnings', "WARNING", clobber=False)
    chip.set('tool', tool, 'regex', step, index, 'errors', "ERROR", clobber=False)

    # reports
    logfile = f"{step}.log"
    for metric in chip.getkeys('metric', 'default', 'default'):
        if metric not in ('runtime', 'memory',
                          'luts', 'dsps', 'brams'):
            chip.set('tool', tool, 'report', step, index, metric, logfile)

################################
# Version Check
################################

def parse_version(stdout):
    # stdout will be in one of the following forms:
    # - 1 08de3b46c71e329a10aa4e753dcfeba2ddf54ddd
    # - 1 v2.0-880-gd1c7001ad
    # - v2.0-1862-g0d785bd84

    # strip off the "1" prefix if it's there
    version = stdout.split()[-1]

    pieces = version.split('-')
    if len(pieces) > 1:
        # strip off the hash in the new version style
        return '-'.join(pieces[:-1])
    else:
        return pieces[0]

def normalize_version(version):
    if '.' in version:
        return version.lstrip('v')
    else:
        return '0'

def pre_process(chip):
    step = chip.get('arg', 'step')

    # Only do diearea inference if we're on floorplanning step and these
    # parameters are all unset.
    if (step != 'floorplan' or
        chip.get('asic', 'diearea') or
        chip.get('asic', 'corearea') or
        chip.valid('input', 'floorplan.def')):
        return

    r = _infer_diearea(chip)
    if r is None:
        return
    diearea, corearea = r

    # TODO: this feels like a hack: putting these here puts them in
    # sc_manifest.tcl, but they don't remain in the manifest in future steps.
    chip.set('asic', 'diearea', diearea)
    chip.set('asic', 'corearea', corearea)

################################
# Post_process (post executable)
################################

def post_process(chip):
    ''' Tool specific function to run after step execution
    '''

    #Check log file for errors and statistics
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    logfile = f"{step}.log"

    # parsing log file
    errors = 0
    warnings = 0
    metric = None

    with open(logfile) as f:
        for line in f:
            metricmatch = re.search(r'^SC_METRIC:\s+(\w+)', line)
            errmatch = re.match(r'^Error:', line)
            warnmatch = re.match(r'^\[WARNING', line)
            area = re.search(r'^Design area (\d+)\s+u\^2\s+(.*)\%\s+utilization', line)
            tns = re.search(r'^tns (.*)', line)
            wns = re.search(r'^wns (.*)', line)
            slack = re.search(r'^worst slack (.*)', line)
            vias = re.search(r'^Total number of vias = (.*).', line)
            wirelength = re.search(r'^Total wire length = (.*) um', line)
            power = re.search(r'^Total(.*)', line)
            if metricmatch:
                metric = metricmatch.group(1)
            elif errmatch:
                errors = errors + 1
            elif warnmatch:
                warnings = warnings +1
            elif area:
                #TODO: not sure the openroad utilization makes sense?
                cellarea = round(float(area.group(1)), 2)
                utilization = round(float(area.group(2)), 2)
                totalarea = round(cellarea/(utilization/100), 2)
                chip.set('metric', step, index, 'cellarea', cellarea, clobber=True)
                chip.set('metric', step, index, 'totalarea', totalarea, clobber=True)
                chip.set('metric', step, index, 'utilization', utilization, clobber=True)
            elif tns:
                chip.set('metric', step, index, 'setuptns', round(float(tns.group(1)), 2), clobber=True)
            elif wns:
                chip.set('metric', step, index, 'setupwns', round(float(wns.group(1)), 2), clobber=True)
            elif slack:
                chip.set('metric', step, index, metric, round(float(slack.group(1)), 2), clobber=True)
            elif wirelength:
                chip.set('metric', step, index, 'wirelength', round(float(wirelength.group(1)), 2), clobber=True)
            elif vias:
                chip.set('metric', step, index, 'vias', int(vias.group(1)), clobber=True)
            elif metric == "power":
                if power:
                    powerlist = power.group(1).split()
                    leakage = powerlist[2]
                    total = powerlist[3]
                    chip.set('metric', step, index, 'peakpower', float(total), clobber=True)
                    chip.set('metric', step, index, 'leakagepower', float(leakage), clobber=True)

    #Setting Warnings and Errors
    chip.set('metric', step, index, 'errors', errors, clobber=True)
    chip.set('metric', step, index, 'warnings', warnings, clobber=True)

    if errors == 0:
        #Temporary superhack!rm
        #Getting cell count and net number from DEF
        with open("outputs/" + chip.design + ".def") as f:
            for line in f:
                cells = re.search(r'^COMPONENTS (\d+)', line)
                nets = re.search(r'^NETS (\d+)', line)
                pins = re.search(r'^PINS (\d+)', line)
                if cells:
                    chip.set('metric', step, index, 'cells', int(cells.group(1)), clobber=True)
                elif nets:
                    chip.set('metric', step, index, 'nets', int(nets.group(1)), clobber=True)
                elif pins:
                    chip.set('metric', step, index, 'pins', int(pins.group(1)), clobber=True)

        # TODO: Uncommented DEF post-processing, probably should only be run for sky130.
        # Basically, we need to cover metal 'pin' data types with 'drawing' data types.
        # Apparently the 'pin' intention is not always manufactured on the final mask.
        # So if we don't add tracks over the pins, we may get open-circuit failures on the die.
        # Easiest way to add a track is in the 'SPECIALNETS' section, with name/net/dimensions
        # taken from the 'PINS' section.
        if step == 'route':
            design = chip.get('design')
            os.rename(f'outputs/{design}.def', f'outputs/{design}-raw.def')
            with open(f'outputs/{design}-raw.def') as f:
              with open(f'outputs/{design}.def', 'w') as wf:
                in_pins = 0
                in_pin = ''
                in_net = ''
                in_layer = ''
                pin_w = 0
                pin_h = 0
                pin_locs = {}

                for line in f:
                    l = line
                    if not in_pins:
                      wf.write(l)
                      if l.strip().startswith('PINS'):
                          in_pins = 1
                    elif in_pins == 1:
                      wf.write(l)
                      if l.strip().startswith('END PINS'):
                        in_pins = 2
                      elif l.strip().startswith('-'):
                        la = l.strip().split()
                        in_pin = la[1]
                        in_net = la[4]
                      # TODO: We should not use hardcoded prefixes for power nets to ignore.
                      elif ('LAYER' in l) and (not 'vcc' in in_pin) and (not 'vss' in in_pin):
                        la = l.strip().split()
                        in_layer = la[2]
                        pin_w = abs(int(la[8]) - int(la[4]))
                        pin_h = abs(int(la[9]) - int(la[5]))
                      elif ('PLACED' in l) and (not 'vcc' in in_pin) and (not 'vss' in in_pin):
                        la = l.strip().split()
                        pin_locs[in_pin] = {'layer': in_layer, 'net': in_net, 'x': int(la[3]), 'y': int(la[4]), 'w': pin_w, 'h': pin_h}
                    elif in_pins == 2:
                      if l.strip().startswith('SPECIALNETS'):
                        la = l.strip().split()
                        numnets = int(la[1]) + len(pin_locs)
                        wf.write('SPECIALNETS %i ;\n'%numnets)
                      # (There may not be a SPECIALNETS section in the DEF output)
                      elif l.strip().startswith('END NETS'):
                        wf.write(l)
                        numnets = len(pin_locs)
                        wf.write('SPECIALNETS %i ;\n'%numnets)
                      elif (l.strip() == 'END SPECIALNETS') or (l.strip() == 'END DESIGN'):
                        for k, v in pin_locs.items():
                          ml = 0
                          if v['layer'] == 'met2':
                            ml = v['w']
                            xl = v['x']
                            xr = v['x']
                            yb = int(v['y'] - v['h'] / 2)
                            yu = int(v['y'] + v['h'] / 2)
                          elif v['layer'] == 'met3':
                            ml = v['h']
                            xl = int(v['x'] - v['w'] / 2)
                            xr = int(v['x'] + v['w'] / 2)
                            yb = v['y']
                            yu = v['y']
                          wf.write('    - %s ( PIN %s ) + USE SIGNAL\n'%(v['net'], k))
                          wf.write('      + ROUTED %s %i + SHAPE STRIPE ( %i %i ) ( %i %i )\n'%(v['layer'], int(ml), xl, yb, xr, yu))
                          wf.write('      NEW %s %i + SHAPE STRIPE ( %i %i ) ( %i %i ) ;\n'%(v['layer'], int(ml), xl, yb, xr, yu))
                        if l.strip() == 'END DESIGN':
                          wf.write('END SPECIALNETS\n')
                        wf.write(l)
                        in_pins = 3
                      else:
                        wf.write(l)
                    elif in_pins == 3:
                      wf.write(l)

    if step == 'sta':
        # Copy along GDS for verification steps that rely on it
        shutil.copy(f'inputs/{chip.design}.gds', f'outputs/{chip.design}.gds')

    #Return 0 if successful
    return 0



##################################################
if __name__ == "__main__":

    chip = make_docs()
    chip.write_manifest("openroad.json")
