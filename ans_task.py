from psychopy import visual, event, core
import time
import json
import numpy as np
from datetime import datetime 

# Set to True when using the stimulus presentation
# device that uses a parallel port to send triggers
# Comment out this line to use triggers
USE_PARALLEL_PORT = False
# Uncomment this line to use triggers
# USE_PARALLEL_PORT = True

_random = np.random.RandomState(None)

trialClock = core.Clock()

win = visual.Window(size=(1000, 1000), fullscr=True, color='white')

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
            pass
        def setPortAddress(self, address):
            pass

    parallel = Parallel()

# copied from previous Psychopy trigger code
parallel.setPortAddress(address=0x0378)

results_date_time_stamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

def load_stimuli(filename='stimuli.json'):
    'Load the ANS task stimuli'
    with open(filename, 'r') as f:
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
        parallel.setData(2)

        while True:

            left_display.draw()
            right_display.draw()

            win.flip()

            # listen for key press
            keys_pressed = event.getKeys()
            if len(keys_pressed) > 0:  # at least one key was pressed
                key_pressed = keys_pressed[0]
                if key_pressed in ('left', 'right'):
                    # Dot display response trigger
                    if key_pressed == 'left':
                        parallel.setData(4) # left key pressed
                    elif key_pressed == 'right':
                        parallel.setData(6) # right key pressed

                    break
        
        

        rt_time = time.time() - start_time_time
        rt_clock = trialClock.getTime() - start_time_clock

        results.append([left_uid, right_uid, left_number_circles, right_number_circles,
                        key_pressed, rt_time, rt_clock])

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
        parallel.setData(8)

        while True:

            left_display.draw()
            right_display.draw()

            win.flip()

            # listen for key press
            keys_pressed = event.getKeys()
            if len(keys_pressed) > 0:  # at least one key was pressed
                key_pressed = keys_pressed[0]
                if key_pressed in ('left', 'right'):
                    # Blob display response trigger
                    # Trigger codes for left/right same as for dot displays
                    if key_pressed == 'left':
                        parallel.setData(4) # left key pressed
                    elif key_pressed == 'right':
                        parallel.setData(6) # right key pressed

                    break

        rt_time = time.time() - start_time_time
        rt_clock = trialClock.getTime() - start_time_clock

        results.append([left_uid, right_uid, left_blob_area, right_blob_area,
                        key_pressed, rt_time, rt_clock])

    return results

#=============================================================================

blocks_stimuli = load_stimuli()

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

def show_instructions(text):

    instrtext.setText(text)

    while True:
        instrtext.draw()
        win.flip()
        # listen for key press
        keys_pressed = event.getKeys()
        if len(keys_pressed) > 0:  # at least one key was pressed
            break


show_instructions(INSTRUCTIONS_TEXT_1)
show_instructions(INSTRUCTIONS_TEXT_2)


dots_blobs_order = ['dots', 'blobs']
RESULTS = []
for k, block_stimuli in enumerate(blocks_stimuli):
    
    # Block start trigger
    parallel.setData(0)

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
    with open(results_date_time_stamp + '_results.json', 'w') as f:
        json.dump(RESULTS, f, indent=4)
    
    if k + 1 < len(blobs_stimuli):
        # Inter-block countdown trigger
        parallel.setData(10)
        countdown(tics = 100)

show_block_start('Experiment completed.')