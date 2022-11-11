from dtw import dtw
import numpy as np


def euclidean_dist(a, b):
    return np.linalg.norm(np.array(a) - np.array(b), ord=2)


def interpolate_point_pair(v1, v2, t):
    """
    interpolate between two points

    Args:
        v1: point 1
        v2: point 2
        t: parameterized variable

    Returns:

    """
    return tuple((1 - t) * x1 + t * x2 for x1, x2 in zip(v1, v2))


def interpolate_trajectory(trajectory, n):
    """
    given a trajectory, produces n points uniformly along the trajectory

    Args:
        trajectory: path
        n: number of points

    Returns:

    """
    num_points = len(trajectory)

    accum_seg_lens = [0]
    for i in range(1, num_points):
        accum_seg_lens.append(accum_seg_lens[-1] + euclidean_dist(trajectory[i - 1], trajectory[i]))
    # normalize accum_seg_lens
    for i in range(len(accum_seg_lens)):
        accum_seg_lens[i] /= accum_seg_lens[-1]

    # determine segment to use at each point
    seg = 0
    for i in range(n + 1):
        total_percent = i / n
        if total_percent > accum_seg_lens[seg + 1]:
            seg += 1
        assert seg < len(accum_seg_lens) - 1  # if accum_seg_lens was computed properly, this should never be broken
        t = (total_percent - accum_seg_lens[seg]) / (accum_seg_lens[seg + 1] - accum_seg_lens[seg])
        yield interpolate_point_pair(trajectory[seg], trajectory[seg + 1], t)


def compute_uniform_cdtw(path1, path2, success_dist, num_points=50, return_dtw=False):
    """
    computes ndtw between two paths by resampling points uniformly along the trajectory
    Args:
        path1:
        path2:
        success_dist:
        num_points:

    Returns:

    """
    adj_path1 = list(interpolate_trajectory(path1, num_points))
    adj_path2 = list(interpolate_trajectory(path2, num_points))

    return compute_ndtw(adj_path1, adj_path2, success_dist, return_dtw)


def compute_ndtw(query, ref, success_dist, return_dtw=False):
    """
    computes normalized dynamic time warping metric
    Args:
        query:
        ref:
        success_dist:

    Returns:

    """
    dtw_dist, cost_matrix, acc_cost_matrix, path = dtw(query, ref, dist=euclidean_dist)

    nDTW = np.exp(-(dtw_dist / (len(ref) * success_dist)))

    if return_dtw:
        return nDTW, dtw_dist

    return nDTW
