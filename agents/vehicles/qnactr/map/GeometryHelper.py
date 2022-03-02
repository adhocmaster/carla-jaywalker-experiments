
from shapely.geometry import LineString

class GeometryHelper():

    @staticmethod
    def create_linestring_from_global_plan(global_plan):
        coordinate_2D = []
        for wp, _ in global_plan:
            location = wp.transform.location
            coordinate_2D.append((location.x, location.y))
            pass
        return LineString(coordinate_2D)
        pass

    @staticmethod
    def is_intersecting(global_plan1, global_plan2):
        line_string1 = GeometryHelper.create_linestring_from_global_plan(global_plan1)
        line_string2 = GeometryHelper.create_linestring_from_global_plan(global_plan2)
        return GeometryHelper.find_intersection_between_two_linestrings(line_string1, line_string2)


    @staticmethod
    def find_intersection_between_two_linestrings(line1, line2):
        intersection = line1.intersection(line2)
        return intersection 

    def create_polyline_from_global_plan(global_plan):
        for i in global_plan:
            print(i)
        pass

# if __name__ == '__main__':

#     points_a = [(1,1),(1,0), (1,-1)]
#     points_b = [(-3, -3), (0,0), (2,2), (-2,-2)]
#     GeometryHelper.find_intersection_between_two_polyline(points_a, points_b)

    