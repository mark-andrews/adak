from collections import OrderedDict
import hashlib

import numpy as np
from numpy import array
from numpy.random import rand, uniform, randint
from math import radians
from scipy.spatial import ConvexHull

maxint = np.iinfo(np.int32).max


class Circle(object):

    def __init__(self, radius_range=[0.05, 0.1], bounding_circle=None, seed=None):

        if seed:
            np.random.seed(seed)

        if not bounding_circle:
            bounding_circle = BoundingCircle()

        self.bounding_circle = bounding_circle
        self.radius_range = radius_range

        self.x, self.y, self.radius = self.random_circle()

    def random_circle(self):

        def euclidean_distance(x):
            return np.sqrt(np.square(self.bounding_circle.center - x).sum())

        while True:

            center = np.empty(2)
            center[0] = uniform(*self.bounding_circle.square[0])
            center[1] = uniform(*self.bounding_circle.square[1])

            radius = uniform(*self.radius_range)

            if euclidean_distance(center) + radius < self.bounding_circle.radius:
                return tuple(center) + (radius,)

    @property
    def center(self):
        return (self.x, self.y)

    def collision(self, other_circle):

        # Is distance between two circle less than sum of radii

        distance = np.sqrt((self.x - other_circle.x)**2 +
                           (self.y - other_circle.y)**2)

        if distance < self.radius + other_circle.radius:
            return True

    @property
    def perimeter_points(self):

        points = []
        for i in range(360):

            phi = radians(i)
            rho = self.radius

            offset_x, offset_y = polar2cartesian(rho, phi)

            points.append((self.x + offset_x, self.y + offset_y))

        return array(points)

    @property
    def parameters(self):
        return (self.x, self.y, self.radius)

    @property
    def area(self):
        return np.pi * self.radius**2


class BoundingCircle(object):

    def __init__(self, x=0.0, y=0.0, radius=1.0):

        self.x = x
        self.y = y
        self.radius = radius

    @property
    def center(self):
        return array((self.x, self.y))

    @property
    def area(self):
        return np.pi * self.radius**2

    @property
    def square(self):

        return ((self.x - self.radius, self.x + self.radius),
                (self.y - self.radius, self.y + self.radius))

    @property
    def parameters(self):
        return self.x, self.y, self.radius


def polar2cartesian(rho, phi):

    x = rho * np.cos(phi)
    y = rho * np.sin(phi)

    return x, y


class RandomDotDisplay:

    """
    Generate a random dot display

    """

    maxint = np.iinfo(np.int32).max

    def __init__(self, K, radius_range=[0.05, 0.1], bounding_circle=None, seed=None):

        self.seed = seed
        self._random = np.random.RandomState(self.seed)
        self._randints = {}

        if not bounding_circle:
            bounding_circle = BoundingCircle()

        self.bounding_circle = bounding_circle
        self.radius_range = radius_range

        self.K = K

        self.uid = self.make_uid()

        self.generate()

    def make_uid(self):

        # If seed is None, then use a random number in uid
        if self.seed is None:
            _seed = rand()
        else:
            _seed = self.seed

        _uid = '_'.join(map(str,
                            [_seed,
                             self.radius_range,
                             self.K,
                             self.bounding_circle.center,
                             self.bounding_circle.radius]))

        return checksum(_uid.encode('utf-8'))[:7]

    def generate_seed(self):

        while True:
            _randint = self._random.randint(self.maxint, dtype=np.int32)
            if _randint not in self._randints:
                break

        self._randints[_randint] = None

        return _randint

    def generate(self):

        circles = []

        while len(circles) < self.K:

            seed = self.generate_seed()

            circle = Circle(self.radius_range, self.bounding_circle, seed)

            if not any([circle.collision(other_circle) for other_circle in circles]):
                circles.append(circle)

        self.circles = circles

    @property
    def centers(self):
        return [circle.center for circle in self.circles]

    @property
    def perimeter_points(self):
        return np.vstack([circle.perimeter_points for circle in self.circles])

    @property
    def convex_hull(self):

        return ConvexHull(self.perimeter_points)

    @property
    def convex_hull_area(self):
        '''
        Area of convex hull of 2d object is the volume
        '''

        return self.convex_hull.volume / self.bounding_circle.area

    @property
    def density(self):
        return sum([circle.area for circle in self.circles]) / self.bounding_circle.area
    
    @property
    def convex_hull_vertices(self):
        points = array(self.perimeter_points)
        hull = self.convex_hull

        vertices = np.hstack((hull.vertices, hull.vertices[0]))

        return points[vertices]

    def plot(self, show_hull=False, width=6, height=6, alpha=0.2, background_colour='red'):

        fig = pyplot.figure(figsize=(width, height))

        ax = pyplot.gca()
        ax.set_xlim(self.bounding_circle.square[0])
        ax.set_ylim(self.bounding_circle.square[1])

        for circle in self.circles:
            circle_patch = pyplot.Circle(
                circle.center, circle.radius, color='blue')
            ax.add_artist(circle_patch)

        circle = pyplot.Circle(self.bounding_circle.center,
                               self.bounding_circle.radius,
                               color=background_colour,
                               alpha=alpha)

        ax.add_artist(circle)

        if show_hull:
            points = array(self.perimeter_points)
            hull = self.convex_hull

            vertices = np.hstack((hull.vertices, hull.vertices[0]))

            pyplot.plot(points[vertices, 0], points[vertices, 1], 'r--', lw=2)

    @classmethod
    def create(cls, **kwargs):

        random_dot_display = cls(**kwargs)

        D = OrderedDict()

        D['uid'] = random_dot_display.uid
        D['seed'] = random_dot_display.seed
        D['bounding_circle_parameters'] = random_dot_display.bounding_circle.parameters
        D['bounding_circle_area'] = random_dot_display.bounding_circle.area

        D['number_of_circles'] = len(random_dot_display.circles)
        D['radius_range'] = random_dot_display.radius_range
        D['convex_hull_proportion'] = random_dot_display.convex_hull_area
        D['density'] = random_dot_display.density

        D['circles'] = [circle.parameters for circle in random_dot_display.circles]

        return D


def make_random_dot_displays(N,
                             number_of_dots_range=(40, 60),
                             radius_range=[0.05, 0.15],
                             bounding_circle_parameters=(0, 0, 1.0),
                             seed=None):
    """
    Make a set of N random dot stimuli
    """

    _random = np.random.RandomState(seed)

    bounding_circle = BoundingCircle(*bounding_circle_parameters)

    kwargs = dict(radius_range=radius_range,
                  bounding_circle=bounding_circle)

    stimuli = []
    for i in range(N):

        kwargs['K'] = _random.randint(*number_of_dots_range)

        seed_circle = _random.randint(maxint)

        stimuli.append(RandomDotDisplay.create(seed=seed_circle, **kwargs))

    return stimuli


def checksum(argument, algorithm='sha1'):
    '''
    Returns the hash checksum of `argument'.
    By default, it will be the sha1 checksum (and so equivalent to linux's
    sha1sum). Alternatively, the algorithm could be md5 (equivalent to linux's
    md5sum), or else sha224, sha256, sha384, sha512.
    '''

    h = hashlib.new(algorithm)

    h.update(argument)

    return h.hexdigest()

def make_blob_display_stimuli(N, number_of_dots_range=(12, 13), radius_range=(0.1, 0.2), seed=None):
    
    _random = np.random.RandomState(seed)

    def sample_display():

        K = _random.randint(*number_of_dots_range)

        seed_circle = _random.randint(maxint)

        return RandomDotDisplay(K=K, radius_range=radius_range, seed=seed_circle)
    
    stimuli = {}
    displays = {}

    while len(stimuli) < N:

        left_blob, right_blob = sample_display(), sample_display()

        # areas to the left and right should be different
        if left_blob.convex_hull_area == right_blob.convex_hull_area:
            continue

        # don't repeat pairs already collected
        if (left_blob.uid, right_blob.uid) in stimuli:
            continue

        stimuli[(left_blob.uid, right_blob.uid)] = None
        displays[left_blob.uid] = dict(vertices = left_blob.convex_hull_vertices.tolist(), area = left_blob.convex_hull_area)
        displays[right_blob.uid] = dict(vertices = right_blob.convex_hull_vertices.tolist(), area = right_blob.convex_hull_area)

    return dict(stimuli = list(stimuli.keys()), displays = displays)    


def make_dot_display_stimuli(N, number_of_dots_range=(40, 60), radius_range=(0.05, 0.1), seed=None):
    """
    Generate a set of N unique pairs of random dot displays.
    """

    _random = np.random.RandomState(seed)

    def sample_display():

        K = _random.randint(*number_of_dots_range)

        seed_circle = _random.randint(maxint)

        return RandomDotDisplay.create(K=K, radius_range=radius_range, seed=seed_circle)

    def display_filter(display, eps=0.01, convex_threshold=0.86, density_threshold=0.38):

        a = abs(display['convex_hull_proportion'] - convex_threshold) < eps/2
        b = abs(display['density'] - density_threshold) < eps

        return a and b
    
    stimuli = {}
    displays = {}

    while len(stimuli) < N:

        left, right = sample_display(), sample_display()

        # numbers to the left and right should be different
        if left['number_of_circles'] == right['number_of_circles']:
            continue

        # we need both displays to have similar densities and hull proportions
        if not display_filter(left) and display_filter(right):
            continue

        # don't repeat pairs already collected
        if (left['uid'], right['uid']) in stimuli:
            continue

        uid_left, uid_right = left.pop('uid'), right.pop('uid')

        stimuli[(uid_left, uid_right)] = None
        displays[uid_left] = left
        displays[uid_right] = right

    return dict(stimuli = list(stimuli.keys()), displays = displays)


if __name__ == '__main__':


    import json
    import argparse
    parser = argparse.ArgumentParser(prog='generate_ans_stimuli',
                                     description='Generate a json file of stimuli for an ANS task.')
    
    parser.add_argument('-b', '--blocks', dest='blocks', default=2, type=int, required=False, help = 'The number of blocks default: 2). Each block has dots and blobs.')
    parser.add_argument('-n', '--number', dest='number', default=10, type=int, required=False, help = 'The number of stimuli to generate (default: 10).')
    parser.add_argument('-s', '--seed', required=False, default=None, type=int, help='The seed for the random number generator (default: None).')
    parser.add_argument('-f', '--filename', default='stimuli.json', required=False, help='The json filename (default: stimuli.json)')

    args = parser.parse_args()
    
    block_stimuli = []
    for block in range(args.blocks):
        dot_stimuli = make_dot_display_stimuli(N = args.number, seed=args.seed)
        blob_stimuli = make_blob_display_stimuli(N = args.number, seed=args.seed)

        stimuli = dict(dots = dot_stimuli, blobs = blob_stimuli)

        block_stimuli.append(stimuli)

    with open(args.filename, 'w') as f:
        json.dump(block_stimuli, f, indent=4)

    