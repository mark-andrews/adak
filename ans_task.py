from psychopy import visual, event, core, gui
import inspect
import time
import json
import numpy as np
from datetime import datetime 


# ============================= Parameters ====================================================

results_date_time_stamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

# ============================= Dialog Box =====================================================

expInfo = {'Participant ID': '',
           'Stimuli file': ['stimuli_4_50_1010101', 'stimuli_4_5_1010101'],
           'Break duration': [100, 10, 5],# Number of seconds for the break between blocks; set to around 100 for real thing
           'Fullscreen': True, # Use fullscreen? Best to set to True for real thing
           'Parallel port': True, # Set to True when using the stimulus presentation
           'Age': list(range(18, 81)),
           'Handedness': ['Right', 'Left', 'Both'],
           'Gender': ['Female', 'Male', 'Non-binary', 'Prefer not to say'],
           'ISI': [1.0, 2.0, 3.0, 5.0],
           'Trial timeout': [5, 1, 0.5]}# Number of seconds before trial times out and moves on

dlg = gui.DlgFromDict(dictionary=expInfo, 
                        title='ANS Task Experiment', 
                        order = ['Participant ID', 
                                'Age',
                                'Gender',
                                'Handedness',
                                'Stimuli file', 
                                'Break duration', 
                                'Trial timeout', 
                                'ISI', 
                                'Fullscreen', 
                                'Parallel port'])

if dlg.OK == False:
    core.quit()

TRIAL_TIMEOUT = float(expInfo['Trial timeout'])
BREAK_DURATION = int(expInfo['Break duration'])
STIMULI_FILENAME = expInfo['Stimuli file']
USE_FULLSCREEN = expInfo['Fullscreen']
USE_PARALLEL_PORT = expInfo['Parallel port']
ISI = float(expInfo['ISI']) # probably should be around 1

# ============================= Set up =====================================================

_random = np.random.RandomState(None)

trialClock = core.Clock()

win = visual.Window(size=(1000, 1000), fullscr=USE_FULLSCREEN, color='white')

width, height = win.size
LEFT_CENTRE = -width / 4
RIGHT_CENTRE = width / 4
SCALE = 0.8 * width / 4
BLOB_SCALE = width / 4

if USE_PARALLEL_PORT:
    from psychopy import parallel
else:
    # Used to disable parallel port during development.
    # Basically, port functions are ignored.
    class Parallel(object):
        def setData(self, x):
            print('Trigger: ' + str(x))
        def setPortAddress(self, address):
            pass

    parallel = Parallel()

# copied from previous Psychopy trigger code
parallel.setPortAddress(address=0x0378)

# ============================== Trigger codes =============================================

trigger_dict = dict(start_experiment = 20,
                    end_experiment = 24,
                    start_block = 4,
                    end_block = 5,
                    show_instructions = 6,
                    start_dot_trial = 8,
                    start_blob_trial = 10,
                    left_response = 12,
                    right_response = 14,
                    no_response = 18)

def fire_trigger(label):
    parallel.setData(trigger_dict[label])


# ============================= UTILS ==========================================================

def this_module_as_string():
    'Return this module as a compressed string'
    with open(inspect.stack()[-1].filename, 'r') as f:
        return f.read()


def load_stimuli(filename='stimuli'):
    'Load the ANS task stimuli'
    with open(filename + '.json', 'r') as f:
        stimuli = json.load(f)

    return stimuli

class BlobDisplayObject:

    def __init__(self, vertices, window, centre, scale) -> None:

        vertices = np.array([[centre, 0]]) + np.array(vertices) * BLOB_SCALE

        self.blob = visual.ShapeStim(
            window,
            vertices=vertices,
            interpolate=True,
            fillColor='black', units='pix')

    def draw(self):
        self.blob.draw()


class DotDisplayObject:

    def __init__(self, circles, window, centre, scale, colour='black') -> None:

        self.dot_display_object = []
        for circle in circles:
            x, y, r = circle
            self.dot_display_object.append(
                visual.Circle(window,
                              pos=(x * scale + centre, y * scale),
                              fillColor=colour,
                              radius=r * scale,
                              units='pix')
            )

    def draw(self):
        [_.draw() for _ in self.dot_display_object]
        return None


def show_dots(dots_stimuli):

    results = []
    for left_uid, right_uid in dots_stimuli['stimuli']:

        # these two displays take around 1 second to draw
        left_display = DotDisplayObject(circles=dots_stimuli['displays'][left_uid]['circles'],
                                        window=win,
                                        centre=LEFT_CENTRE,
                                        scale=SCALE)

        right_display = DotDisplayObject(circles=dots_stimuli['displays'][right_uid]['circles'],
                                         window=win,
                                         centre=RIGHT_CENTRE,
                                         scale=SCALE)

        left_number_circles = dots_stimuli['displays'][left_uid]['number_of_circles']
        right_number_circles = dots_stimuli['displays'][right_uid]['number_of_circles']

        start_time_clock = trialClock.getTime()
        start_time_time = time.time()

        event.clearEvents()

        # Dot display trial start trigger
        fire_trigger('start_dot_trial')

        while True:

            left_display.draw()
            right_display.draw()

            win.flip()

            # listen for key press
            keys_pressed = event.getKeys()
            if len(keys_pressed) > 0:  # at least one key was pressed
                key_pressed = keys_pressed[0]
                if key_pressed in ('left', 'right', 'escape'):
                    # Dot display response trigger
                    if key_pressed == 'left':
                        fire_trigger('left_response')
                    elif key_pressed == 'right':
                        fire_trigger('right_response')
                    else:
                        core.quit()

                    break
            
            if time.time() - start_time_time > TRIAL_TIMEOUT:
                key_pressed = None
                fire_trigger('no_response') # No response, timeout
                break
        
        

        rt_time = time.time() - start_time_time
        rt_clock = trialClock.getTime() - start_time_clock

        results.append(dict(left_uid=left_uid,
                            right_uid=right_uid,
                            left_size=left_number_circles,
                            right_size=right_number_circles,
                            key_pressed=key_pressed,
                            rt_time=rt_time,
                            rt_clock=rt_clock))
        
        add_isi(win, ISI) # Interval stimulus interval

    return results


def show_blobs(blobs_stimuli):

    results = []
    for left_uid, right_uid in blobs_stimuli['stimuli']:

        left_display = BlobDisplayObject(vertices=blobs_stimuli['displays'][left_uid]['vertices'],
                                         window=win,
                                         centre=LEFT_CENTRE,
                                         scale=SCALE)

        right_display = BlobDisplayObject(vertices=blobs_stimuli['displays'][right_uid]['vertices'],
                                          window=win,
                                          centre=RIGHT_CENTRE,
                                          scale=SCALE)

        left_blob_area = blobs_stimuli['displays'][left_uid]['area']
        right_blob_area = blobs_stimuli['displays'][right_uid]['area']

        start_time_clock = trialClock.getTime()
        start_time_time = time.time()

        event.clearEvents()
        
        # Blob display trial start trigger
        fire_trigger('start_blob_trial')

        while True:

            left_display.draw()
            right_display.draw()

            win.flip()

            # listen for key press
            keys_pressed = event.getKeys()
            if len(keys_pressed) > 0:  # at least one key was pressed
                key_pressed = keys_pressed[0]
                if key_pressed in ('left', 'right', 'escape'):
                    # Blob display response trigger
                    # Trigger codes for left/right same as for dot displays
                    if key_pressed == 'left':
                        # left key pressed
                        fire_trigger('left_response')
                    elif key_pressed == 'right':
                        # right key pressed
                        fire_trigger('right_response')
                    else:
                        core.quit()

                    break

            if time.time() - start_time_time > TRIAL_TIMEOUT:
                key_pressed = None
                fire_trigger('no_response')
                break

        rt_time = time.time() - start_time_time
        rt_clock = trialClock.getTime() - start_time_clock

        results.append(dict(left_uid=left_uid,
                            right_uid=right_uid,
                            left_size=left_blob_area,
                            right_size=right_blob_area,
                            key_pressed=key_pressed,
                            rt_time=rt_time,
                            rt_clock=rt_clock))
        
        add_isi(win, ISI) # Interval stimulus interval

    return results


def show_block_start(text='Block'):
    start_time = time.time()
    start_text.setText(text)
    while True:
        start_text.draw()
        win.flip()

        if time.time() - start_time > 2:
            break

def countdown(tics = 100):

    start_time = time.time()
    
    while True:

        time_elapsed = time.time() - start_time
        instrtext.setText(COUNTDOWN % (tics - time_elapsed))
        instrtext.draw()
        win.flip()

        if time_elapsed > tics:
            break

        keys_pressed = event.getKeys()
        if len(keys_pressed) > 0:  # at least one key was pressed
            if keys_pressed[0] == 'escape':
                core.quit()
            break


def add_isi(win, duration):
    'Add a blank screen for `duration` seconds'
    isi_start_time = trialClock.getTime()
    while True:
        win.flip()
        if trialClock.getTime() - isi_start_time >= duration:
            break


def show_instructions(text):

    instrtext.setText(text)

    while True:
        instrtext.draw()
        win.flip()
        # listen for key press
        keys_pressed = event.getKeys()
        if len(keys_pressed) > 0:  # at least one key was pressed
            if keys_pressed[0] == 'escape':
                core.quit()
            break


#=============================================================================

blocks_stimuli = load_stimuli(filename=STIMULI_FILENAME)

INSTRUCTIONS_TEXT_1 = '''
In this experiment, on each trial, you will be shown
either two sets of dots, or two black iregular shapes.

When shown the dots, your task will be say which set
has more dots: left or right.

When shown the shapes, your task will be say which one
is larger.

Press any key to move on to next instructions page.
'''

INSTRUCTIONS_TEXT_2 = '''
There are %d blocks of trials in the experiment.

Each block of trials shows a set of dots and a set
of shapes trials.

In each block, there are %d dots and %d shapes trials.

In each block, you will be reminded of the task instructions.

Press any key to begin the first block.
''' % (len(blocks_stimuli), 
       len(blocks_stimuli[0]['dots']['stimuli']),
       len(blocks_stimuli[0]['blobs']['stimuli']))
           

DOTS_INSTRUCTIONS_TEXT = '''
You are now going to be shown %d dots trials.

Each trial will show two sets of dots side by side.

Your task will be say which set has more dots.

If you think the set of the left has more dots, press
the "left" key. 

If you think the set of the right has more dots, press
the "right" key. 

Press any key to begin the trials.
''' % (len(blocks_stimuli[0]['dots']['stimuli']))
           
BLOBS_INSTRUCTIONS_TEXT = '''
You are now going to be shown %d shapes trials.

Each trial will show two shapes side by side.

Your task will be say which shape is larger.

If you think the shape of the left is larger, press
the "left" key. 

If you think the shape on the right is larger, press
the "right" key. 

Press any key to begin the trials.
''' % (len(blocks_stimuli[0]['dots']['stimuli']))
           
COUNTDOWN = '''
Take a break before the next trial: %d
'''

start_text = visual.TextStim(win=win, text='Hello', color='black')
instrtext = visual.TextStim(
    win=win, text='INSTRUCTIONS TEXT', font=u'Arial', color='black', height=0.06, alignText='left')

fire_trigger('start_experiment')
show_block_start('Experiment starting.')


fire_trigger('show_instructions')
show_instructions(INSTRUCTIONS_TEXT_1)
show_instructions(INSTRUCTIONS_TEXT_2)


dots_blobs_order = ['dots', 'blobs']

experiment_information = {}
experiment_information['code'] = this_module_as_string()
experiment_information['participant_id'] = expInfo['Participant ID']
experiment_information['participant_gender'] = expInfo['Gender']
experiment_information['participant_age'] = expInfo['Age']
experiment_information['participant_handedness'] = expInfo['Handedness']
experiment_information['fullscreen'] = USE_FULLSCREEN
experiment_information['stimuli_file'] = expInfo['Stimuli file']
experiment_information['trial_timeout'] = expInfo['Trial timeout']
experiment_information['break_duration'] = expInfo['Break duration']
experiment_information['datetime'] = results_date_time_stamp

RESULTS = [experiment_information]

for k, block_stimuli in enumerate(blocks_stimuli):
    
    # Block start trigger
    fire_trigger('start_block')

    show_block_start('Block %d of %d' % (k+1, len(blocks_stimuli)))

    _random.shuffle(dots_blobs_order)

    for dots_or_blobs in dots_blobs_order:

        if dots_or_blobs == 'dots':
            show_instructions(DOTS_INSTRUCTIONS_TEXT)
            dots_stimuli = block_stimuli['dots']
            results = show_dots(dots_stimuli=dots_stimuli)
            RESULTS.append(dict(block = k +1,
                                type = 'dots',
                                results = results))


        elif dots_or_blobs == 'blobs':
            show_instructions(BLOBS_INSTRUCTIONS_TEXT)
            blobs_stimuli = block_stimuli['blobs']
            results = show_blobs(blobs_stimuli=blobs_stimuli)
            RESULTS.append(dict(block = k +1,
                                type = 'blobs',
                                results = results))


    # write results to file
    with open(expInfo['Participant ID'] + '_' + results_date_time_stamp + '_results.json', 'w') as f:
        json.dump(RESULTS, f, indent=4)

    fire_trigger('end_block')
    
    if k + 1 < len(blocks_stimuli):
        countdown(tics = BREAK_DURATION)

fire_trigger('end_experiment')
show_block_start('Experiment completed.')

