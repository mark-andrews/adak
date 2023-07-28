A Psychopy based Approximate Number System (ANS) task

## Run the experiment

```
python ans_task.py
```

or else in standalone Psychopy, just open that script in the coder and run it.


## How to generate stimuli

The following code generates 4 experimental blocks, each block with 100 dots and 100 blobs, so 800 trials in all.
											
```bash
python generate_ans_stimuli.py --blocks 4 --number 100 --seed 1010101 -f stimuli_4_100_1010101.json
```

The following code generates 4 experimental blocks, each block with 50 dots and 50 blobs, so 400 trials in all.
											
```bash
python generate_ans_stimuli.py --blocks 4 --number 50 --seed 1010101 -f stimuli_4_50_1010101.json
```
