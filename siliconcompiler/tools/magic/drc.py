
from .magic import setup as setup_tool

def setup(chip):
    ''' Helper method to setup DRC-specific configs.
    '''

    # Generic tool setup
    setup_tool(chip)

    tool = 'magic'
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    task = 'drc'
    design = chip.top()

    report_path = f'reports/{design}.drc'
    chip.set('tool', tool, 'task', task, 'report', step, index, 'drvs', report_path)

################################
# Post_process (post executable)
################################

def post_process(chip):
    ''' Tool specific function to run after step execution

    Reads error count from output and fills in appropriate entry in metrics
    '''

    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    design = chip.top()

    report_path = f'reports/{design}.drc'
    with open(report_path, 'r') as f:
        for line in f:
            errors = re.search(r'^\[INFO\]: COUNT: (\d+)', line)

            if errors:
                chip.set('metric', step, index, 'drvs', errors.group(1))

    #TODO: return error code
    return 0
