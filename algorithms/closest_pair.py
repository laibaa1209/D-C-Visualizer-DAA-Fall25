import math

def parse_points_file_content(content: str):
    points = []
    lines = content.strip().splitlines()

    # Case 1: First line is N (# of points)
    try:
        first = lines[0].strip().split()
        if len(first) == 1 and first[0].isdigit():
            N = int(first[0])
            for line in lines[1:1+N]:
                try:
                    x, y = map(float, line.split())
                    points.append((x, y))
                except:
                    continue
            return points
    except:
        pass

    # Case 2: Format is just many "x y" lines
    for line in lines:
        try:
            x, y = map(float, line.strip().split())
            points.append((x, y))
        except:
            continue

    return points


# ----------------------------- DIVIDE AND CONQUER IMPLEMENTATION -----------------------------
def closest_pair(points, visualize=False):
    """Divide-and-conquer closest pair algorithm with visualization."""
    
    if len(points) < 2:
        if visualize:
            yield {
                "type": "result",
                "pair": None,
                "best": float('inf')
            }
        return None, float('inf')
    
    # Store original points list for visualization
    original_points = points.copy()
    
    # Sort points by x-coordinate
    points_sorted_x = sorted(points, key=lambda p: p[0])
    
    def _closest_pair_rec(pts, orig_pts):
        """Recursive helper function."""
        n = len(pts)
        
        # Base case: brute force for small sets
        if n <= 3:
            min_d = float('inf')
            best_pair = None
            
            if visualize and n > 1:
                yield {
                    "type": "bruteforce",
                    "points": pts,
                    "best": float('inf')
                }
            
            for i in range(n):
                for j in range(i+1, n):
                    d = math.dist(pts[i], pts[j])
                    
                    if visualize:
                        yield {
                            "type": "compare",
                            "pair": (pts[i], pts[j]),
                            "dist": d
                        }
                    
                    if d < min_d:
                        min_d = d
                        best_pair = (pts[i], pts[j])
            
            if visualize and n > 1:
                yield {
                    "type": "bruteforce",
                    "points": pts,
                    "best": min_d
                }
            
            return best_pair, min_d
        
        # Divide: find the midpoint
        mid = n // 2
        mid_point = pts[mid]
        mid_x = mid_point[0]
        
        left_pts = pts[:mid]
        right_pts = pts[mid:]
        
        # Yield split step
        if visualize:
            yield {
                "type": "split",
                "x": mid_x,
                "left": left_pts,
                "right": right_pts
            }
        
        # Conquer: recursively find closest pairs in left and right
        left_pair, left_d = yield from _closest_pair_rec(left_pts, orig_pts)
        right_pair, right_d = yield from _closest_pair_rec(right_pts, orig_pts)
        
        # Find the minimum distance from recursive calls
        if left_d < right_d:
            min_d = left_d
            best_pair = left_pair
        else:
            min_d = right_d
            best_pair = right_pair
        
        # Combine: check points in the strip
        strip = []
        for pt in pts:
            if abs(pt[0] - mid_x) < min_d:
                strip.append(pt)
        
        # Sort strip by y-coordinate
        strip_sorted_y = sorted(strip, key=lambda p: p[1])
        
        # Check points in strip (only need to check within min_d in y-direction)
        if visualize and len(strip) > 1:
            yield {
                "type": "strip",
                "pair": None,
                "x": mid_x,
                "strip": strip_sorted_y,
                "best": min_d
            }
        
        # Check each point in strip against points within min_d in y-direction
        for i in range(len(strip_sorted_y)):
            # Only check next 7 points (geometric property)
            for j in range(i+1, min(i+8, len(strip_sorted_y))):
                if strip_sorted_y[j][1] - strip_sorted_y[i][1] >= min_d:
                    break
                
                d = math.dist(strip_sorted_y[i], strip_sorted_y[j])
                
                if visualize:
                    yield {
                        "type": "compare",
                        "pair": (strip_sorted_y[i], strip_sorted_y[j]),
                        "dist": d
                    }
                
                if d < min_d:
                    min_d = d
                    best_pair = (strip_sorted_y[i], strip_sorted_y[j])
                    
                    if visualize:
                        yield {
                            "type": "strip",
                            "pair": best_pair,
                            "x": mid_x,
                            "strip": strip_sorted_y,
                            "best": min_d
                        }
        
        return best_pair, min_d
    
    # Call recursive function
    gen = _closest_pair_rec(points_sorted_x, original_points)
    
    # Collect all yields and yield them
    best_pair = None
    best_dist = float('inf')
    
    try:
        while True:
            step = next(gen)
            if isinstance(step, tuple) and len(step) == 2:
                # This is the return value
                best_pair, best_dist = step
                break
            else:
                # This is a yield value
                yield step
    except StopIteration as e:
        # Generator finished, check if there's a return value
        if hasattr(e, 'value') and e.value is not None:
            best_pair, best_dist = e.value
    
    # If we didn't get the result from the generator, compute it
    if best_pair is None or best_dist == float('inf'):
        # Fallback: run the generator again to get the result
        gen = _closest_pair_rec(points_sorted_x, original_points)
        result = None
        try:
            while True:
                step = next(gen)
                if not isinstance(step, dict):
                    result = step
                    break
        except StopIteration as e:
            if hasattr(e, 'value') and e.value is not None:
                result = e.value
        
        if result:
            best_pair, best_dist = result
    
    # Yield final result
    if visualize:
        yield {
            "type": "result",
            "pair": best_pair,
            "best": best_dist
        }
    
    return best_pair, best_dist
