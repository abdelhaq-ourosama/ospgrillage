# -*- coding: utf-8 -*-
"""
This module contains the Mesh class which controls the meshing procedure of *ospgrillage*. The mesh class stores
information about the grillage mesh such as nodes, elements, and grids. Additionally, Mesh class provides methods to
mesh grillages, either orthogonal or oblique. Unlike other modules, the constructor of Mesh class is handled exclusively
by OspGrillage class.
"""
import math

from ospgrillage.static import *
from collections import namedtuple


def create_point(**kwargs):
    """
    User interface function to create a point named tuple
    :keyword:

    * x (`float` or `int`): x coordinate
    * y (`float` or `int`): y coordinate. Default = 0 for model plane of grillage
    * z (`float` or `int`): z coordinate

    :return: Point namedTuple
    """
    x = kwargs.get("x", None)
    y = kwargs.get("y", 0)
    z = kwargs.get("z", None)
    return Point(x, y, z)


# named tuple definition
Point = namedtuple("Point", ["x", "y", "z"])


class Mesh:
    """
    Base class for mesh class. The class holds information pertaining the mesh group such as element connectivity and nodes
    of the mesh object. Positional arguments are handled by OspGrillage class.

    .. note::

        As of version 0.1.0, the default mesh is a straight mesh with either Orthogonal and Oblique grids. For developers
        mesh module needs a new structure where the mesh class will have mesh types segregated into a base Mesh class
        and child class e.g. OrthogonalMesh(Mesh) class.

    """

    def __init__(
        self,
        long_dim,
        width,
        trans_dim,
        edge_dist_a,
        edge_dist_b,
        num_trans_beam,
        num_long_beam,
        skew_1,
        skew_2,
        ext_to_int_a,
        ext_to_int_b,
        pt1=Point(0, 0, 0),
        pt2=Point(0, 0, 0),
        pt3=None,
        element_counter=1,
        node_counter=1,
        transform_counter=0,
        global_x_grid_count=0,
        global_edge_count=0,
        mesh_origin=None,
        quad_ele=False,
        **kwargs
    ):

        # inputs from OspGrillage required to create mesh
        self.long_dim = long_dim
        self.trans_dim = trans_dim
        self.edge_width_a = edge_dist_a
        self.edge_width_b = edge_dist_b
        self.ext_to_int_a = ext_to_int_a
        self.ext_to_int_b = ext_to_int_b
        self.width = width
        self.num_trans_beam = num_trans_beam
        self.num_long_beam = num_long_beam
        # variables on angle and mesh type
        self.skew_1 = skew_1
        self.skew_2 = skew_2
        self.orthogonal = kwargs.get("orthogonal", False)
        self.beam_element_flag = kwargs.get(
            "create_beam_elements", True
        )  # bool to create beam elements between nodes
        # sweep path properties
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3
        # counters to keep track of variables
        self.node_counter = node_counter
        self.element_counter = element_counter
        self.transform_counter = transform_counter
        self.global_x_grid_count = global_x_grid_count
        self.global_z_grid_count = None
        # edge construction line variables
        self.global_edge_count = global_edge_count
        self.edge_node_recorder = dict()  # key: node tag, val: unique tag for edge
        # Prefix/ rules variables here
        assigned_node_tag = []
        self.decimal_lim = 3  # variable for floating point arithmetic error
        self.skew_threshold = [11, 30]
        self.curve = False
        self.search_x_inc = 0.001
        # initiate list for nodes and elements
        self.long_ele = []
        self.trans_ele = []
        self.edge_span_ele = []
        self.y_elevation = 0
        self.mesh_design_line = []
        # dict for node and ele transform
        self.transform_dict = dict()  # key: vector xz, val: transform tag
        self.node_spec = (
            dict()
        )  # key: node tag, val: dict of node details - see technical notes
        # variables for curve mesh
        self.curve_center = []
        self.curve_radius = []
        # line / circle equation variables - instantiate
        self.m = 0
        self.c = 0
        self.r = 0
        self.R = 0
        self.d = None  # list of circle centre and circle radius [ c, r]
        # meshing properties
        if mesh_origin is None:
            self.mesh_origin = [0, 0, 0]
        else:
            self.mesh_origin = mesh_origin  # default origin
        # meshing variables
        self.first_connecting_region_nodes = []
        self.end_connecting_region_nodes = []
        self.sweep_nodes = []
        self.z_group_recorder = []
        # quad elements flag
        self.quad_ele = quad_ele
        self.max_grid_dim = None  #
        # rigid link parameters - to be assigned to beam elements representing longitudinal beams
        self.rigid_dist_y = kwargs.get("rigid_dist_y")
        self.rigid_dist_z = kwargs.get("rigid_dist_z")
        self.rigid_dist_x = kwargs.get("rigid_dist_x")
        # ------------------------------------------------------------------------------------------
        # Create sweep path obj
        self.sweep_path = SweepPath(self.pt1, self.pt2, self.pt3)
        (
            self.zeta,
            self.m,
            self.c,
        ) = self.sweep_path.get_sweep_line_properties()  # properties m,c,zeta angle
        # ------------------------------------------------------------------------------------------
        # check condition for orthogonal mesh
        if self.skew_1 != 0:
            self._check_skew(self.skew_1, self.zeta)
        elif self.skew_2 != 0:
            self._check_skew(self.skew_2, self.zeta)

        # check if angle between construction line and sweep path is sufficiently small - if greater meshing will
        # result in overlapping edges (between start and end edge) or edge construction line creating extra nodes on
        # opposite construction lines.
        if self.long_dim < self.width * np.tan(self.skew_1 / 180 * np.pi):
            raise ValueError(
                "insufficent length of grillage - causes one or more overlapping edge with extra longitudinal members"
                "due to skew angle at start edge- try using a smaller angle or larger long_dim"
            )
        elif self.long_dim < self.width * np.tan(self.skew_2 / 180 * np.pi):
            raise ValueError(
                "insufficent length of grillage resulted in overlapping edge with extra longitudinal members"
                "due to skew angle at end edge- try using a smaller angle or larger long_dim"
            )
        # ------------------------------------------------------------------------------------------
        # edge construction line 1
        self.start_edge_line = self.create_control_points(
            edge_ref_point=self.mesh_origin,
            width_z=self.width,
            edge_width_a=self.edge_width_a,
            edge_width_b=self.edge_width_b,
            edge_angle=self.skew_1,
            num_long_beam=self.num_long_beam,
            model_plane_y=self.y_elevation,
            ext_to_int_a=self.ext_to_int_a,
            ext_to_int_b=self.ext_to_int_b,
            **kwargs
        )

        # ------------------------------------------------------------------------------------------
        # edge construction line 2
        end_point_z = self.sweep_path.get_line_function(self.long_dim)
        self.end_edge_line = self.create_control_points(
            edge_ref_point=[self.long_dim, 0, end_point_z],
            width_z=self.width,
            edge_width_a=self.edge_width_a,
            edge_width_b=self.edge_width_b,
            edge_angle=self.skew_2,
            num_long_beam=self.num_long_beam,
            model_plane_y=self.y_elevation,
            ext_to_int_a=self.ext_to_int_a,
            ext_to_int_b=self.ext_to_int_b,
            **kwargs
        )
        # ------------------------------------------------------------------------------------------
        # Sweep nodes
        # nodes to be swept across sweep path varies based
        # sweeping_nodes variable is a list containing x,y,z coordinates which slope is dependant on slope at  ref point
        # of sweep nodes. slope of sweep nodes is always ORTHOGONAL to tangent of sweep path at intersection with ref
        # point
        self.sweeping_nodes = []
        # z coordinate of ref sweep nodes (relative to origin)
        self.noz = self.start_edge_line.noz
        if self.orthogonal:
            self.sweeping_nodes = self._rotate_sweep_nodes(
                self.zeta / 180 * np.pi
            )  # zeta in rad
        else:  # skew
            # sweep line of skew mesh == edge_construction line
            self.sweeping_nodes = self.start_edge_line.node_list
        self.nox = np.linspace(0, self.long_dim, self.num_trans_beam)
        # ------------------------------------------------------------------------------------------
        # create nodes and elements
        # if orthogonal, orthogonal mesh only be slayed onto a curve mesh, if skew mesh curved/arc line segment must be
        # false
        if self.orthogonal:
            # mesh start span construction line region
            self._orthogonal_meshing()

        elif not self.curve:  # Skew mesh + angle
            self._fixed_sweep_node_meshing()

        # run section grouping for longitudinal and transverse members
        self._identify_common_z_group()
        self._identify_member_groups()
        # model plane
        self.model_plane_z_groups = list(self.z_group_to_ele.keys())

    def create_control_points(self, **kwargs):
        # base version creating standard node points of control points - either start or end edge -
        # standard correspond to base model technique - grillage with beam element
        return EdgeControlLine(**kwargs)

    def _fixed_sweep_node_meshing(self):
        assigned_node_tag = []
        previous_node_tag = []
        for x_count, x_inc in enumerate(self.nox):
            for z_count, ref_point in enumerate(self.sweeping_nodes):
                # offset x and y in all points in ref points
                z_inc = np.round(
                    select_segment_function(
                        curve_flag=self.curve,
                        d=self.d,
                        m=self.m,
                        c=self.m,
                        x=x_inc,
                        r=self.r,
                    ),
                    self.decimal_lim,
                )
                node_coordinate = [
                    ref_point[0] + x_inc,
                    ref_point[1],
                    ref_point[2] + z_inc,
                ]
                self.node_spec.setdefault(
                    self.node_counter,
                    {
                        "tag": self.node_counter,
                        "coordinate": node_coordinate,
                        "x_group": x_count,
                        "z_group": z_count,
                    },
                )
                assigned_node_tag.append(self.node_counter)
                self.node_counter += 1
                # link transverse elements
                if z_count > 0:
                    # element list [element tag, node i, node j, x/z group]
                    if not self.beam_element_flag:
                        continue
                    tag = self._get_geo_transform_tag(
                        [assigned_node_tag[z_count - 1], assigned_node_tag[z_count]]
                    )
                    self.trans_ele.append(
                        [
                            self.element_counter,
                            assigned_node_tag[z_count - 1],
                            assigned_node_tag[z_count],
                            x_count,
                            tag,
                        ]
                    )
                    self.element_counter += 1

            # create longitudinal ele by linking assigned nodes @ current step with assigned nodes from previous step
            if x_count == 0:
                previous_node_tag = assigned_node_tag
                # record
                for nodes in previous_node_tag:
                    self.edge_node_recorder.setdefault(nodes, self.global_edge_count)
                self.global_edge_count += 1
            elif x_count > 0:
                for pre_node in previous_node_tag:
                    for cur_node in assigned_node_tag:
                        cur_z_group = self.node_spec[cur_node]["z_group"]
                        prev_z_group = self.node_spec[pre_node]["z_group"]
                        if cur_z_group == prev_z_group:
                            tag = self._get_geo_transform_tag([pre_node, cur_node])
                            self.long_ele.append(
                                [
                                    self.element_counter,
                                    pre_node,
                                    cur_node,
                                    cur_z_group,
                                    tag,
                                ]
                            )
                            self.element_counter += 1
                            break  # break assign long ele loop (cur node)
                # here updates the record for previous node tag step
                previous_node_tag = assigned_node_tag
                if x_count == len(self.nox) - 1:
                    for nodes in previous_node_tag:
                        self.edge_node_recorder.setdefault(
                            nodes, self.global_edge_count
                        )
                    self.global_edge_count += 1
            # reset counter and recorder for next loop x increment
            self.global_x_grid_count += 1
            assigned_node_tag = []

    def _orthogonal_meshing(self):
        """
        Main procedure to mesh nodes (and beam elements) of model based on orthogonal meshing
        """
        global sweep_nodes, z_group_recorder
        self.assigned_node_tag = []
        self.previous_node_tag = []
        self.sweep_path_points = []
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # first edge construction line
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        start_point_x = self.mesh_origin[0]
        start_point_z = self.mesh_origin[2]
        # if skew angle of edge line is below threshold for orthogonal, perform mesh as oblique for edge line
        if np.abs(self.skew_1 + self.zeta) < self.skew_threshold[0]:
            # if angle less than threshold, assign nodes of edge member as it is
            current_sweep_nodes = self.start_edge_line.node_list
            for (z_count_int, nodes) in enumerate(current_sweep_nodes):
                x_inc = start_point_x
                z_inc = start_point_z
                node_coordinate = [nodes[0] + x_inc, nodes[1], nodes[2] + z_inc]
                self.node_spec.setdefault(
                    self.node_counter,
                    {
                        "tag": self.node_counter,
                        "coordinate": node_coordinate,
                        "x_group": self.global_x_grid_count,
                        "z_group": z_count_int,
                    },
                )

                self.assigned_node_tag.append(self.node_counter)
                self.node_counter += 1
                # if loop assigned more than two nodes, link nodes as a transverse member
                if z_count_int > 0:
                    # run sub procedure to assign
                    # self.__assign_transverse_members(pre_node=self.assigned_node_tag[z_count_int - 1],
                    #                                  cur_node=self.assigned_node_tag[z_count_int])
                    if not self.beam_element_flag:
                        continue
                    if len(self.assigned_node_tag) >= 1:
                        self._assign_edge_trans_members(
                            self.assigned_node_tag[z_count_int - 1],
                            self.assigned_node_tag[z_count_int],
                            self.global_edge_count,
                        )
                        # get and link edge nodes from previous and current as skewed edge member
                        self.edge_node_recorder.setdefault(
                            self.assigned_node_tag[z_count_int - 1],
                            self.global_edge_count,
                        )
                        self.edge_node_recorder.setdefault(
                            self.assigned_node_tag[z_count_int], self.global_edge_count
                        )

                if len(self.assigned_node_tag) == len(self.noz):
                    self.first_connecting_region_nodes = self.assigned_node_tag
            self.global_x_grid_count += 1
            self.assigned_node_tag = []  # reset variable
            # print("Edge mesh @ start span completed")
        else:  # perform edge meshing with variable distance between transverse members by looping through all control
            # points of edgecontrolline
            # loop for each control point of edge line with sweep nodes
            for z_count, int_point in enumerate(self.start_edge_line.node_list):
                # search point on sweep path line whose normal intersects int_point.
                ref_point_x, ref_point_z = self._search_x_point(
                    int_point, start_point_x
                )
                # record points
                self.sweep_path_points.append(
                    [ref_point_x, self.y_elevation, ref_point_z]
                )
                # find m' of line between intersect int_point and ref point on sweep path
                m_prime, phi = get_slope(
                    [ref_point_x, self.y_elevation, ref_point_z], int_point
                )
                # rotate sweep line such that parallel to m' line
                # if skew is positive, algorithm may mistake first point as orthogonal 90 deg, specify initial m based
                # on zeta
                if self.skew_1 > 0:
                    angle = np.arctan(self.zeta / 180 * np.pi)
                else:
                    angle = np.pi / 2 - np.abs(phi)
                current_sweep_nodes = self._rotate_sweep_nodes(angle)
                # get z group of first node in current_sweep_nodes - for correct assignment in loop
                z_group = self.start_edge_line.get_node_group_z(int_point)
                # check angle condition, if skew + zeta (offset from plane)
                if 90 + self.skew_1 + self.zeta > 90:
                    sweep_nodes = current_sweep_nodes[z_count:]
                    z_group_recorder = list(range(z_group, len(current_sweep_nodes)))
                elif 90 + self.skew_1 + self.zeta < 90:
                    sweep_nodes = current_sweep_nodes[0 : (z_count + 1)]
                    z_group_recorder = (
                        list(range(0, z_group + 1)) if z_group != 0 else [0]
                    )

                # on each control point, loop through sweeping nodes to create nodes
                for (z_count_int, nodes) in enumerate(sweep_nodes):
                    x_inc = ref_point_x
                    z_inc = ref_point_z
                    node_coordinate = [nodes[0] + x_inc, nodes[1], nodes[2] + z_inc]
                    self.node_spec.setdefault(
                        self.node_counter,
                        {
                            "tag": self.node_counter,
                            "coordinate": node_coordinate,
                            "x_group": self.global_x_grid_count,
                            "z_group": z_group_recorder[z_count_int],
                        },
                    )

                    self.assigned_node_tag.append(self.node_counter)
                    self.node_counter += 1
                    # if loop assigned more than two nodes, link nodes as a transverse member
                    if not self.beam_element_flag:
                        continue
                    if z_count_int > 0:
                        # run sub procedure to assign
                        self._assign_transverse_members(
                            pre_node=self.assigned_node_tag[z_count_int - 1],
                            cur_node=self.assigned_node_tag[z_count_int],
                        )

                if not self.beam_element_flag:
                    continue
                # if loop is in first step, there is only one column of nodes, skip longitudinal assignment
                if z_count == 0:
                    self.previous_node_tag = self.assigned_node_tag
                if z_count > 0:
                    for pre_node in self.previous_node_tag:
                        for cur_node in self.assigned_node_tag:
                            cur_z_group = self.node_spec[cur_node]["z_group"]
                            prev_z_group = self.node_spec[pre_node]["z_group"]
                            if cur_z_group == prev_z_group:
                                self._assign_longitudinal_members(
                                    pre_node=pre_node,
                                    cur_node=cur_node,
                                    cur_z_group=cur_z_group,
                                )
                                break  # break assign long ele loop (cur node)

                    # if angle is positive (slope negative), edge nodes located at the first element of list
                    if len(self.assigned_node_tag) >= 1:
                        if 90 + self.skew_1 + self.zeta > 90:
                            self._assign_edge_trans_members(
                                self.previous_node_tag[0],
                                self.assigned_node_tag[0],
                                self.global_edge_count,
                            )
                            # get and link edge nodes from previous and current as skewed edge member
                            self.edge_node_recorder.setdefault(
                                self.previous_node_tag[0], self.global_edge_count
                            )
                            self.edge_node_recorder.setdefault(
                                self.assigned_node_tag[0], self.global_edge_count
                            )
                        elif 90 + self.skew_1 + self.zeta < 90:
                            self._assign_edge_trans_members(
                                self.previous_node_tag[-1],
                                self.assigned_node_tag[-1],
                                self.global_edge_count,
                            )
                            # get and link edge nodes from previous and current as skewed edge member
                            self.edge_node_recorder.setdefault(
                                self.previous_node_tag[-1], self.global_edge_count
                            )
                            self.edge_node_recorder.setdefault(
                                self.assigned_node_tag[-1], self.global_edge_count
                            )
                    # update recorder for previous node tag step
                    self.previous_node_tag = self.assigned_node_tag
                # update and reset recorders for next column of sweep nodes
                self.global_x_grid_count += 1
                if len(self.assigned_node_tag) == len(self.noz):
                    self.first_connecting_region_nodes = self.assigned_node_tag
                self.ortho_previous_node_column = self.assigned_node_tag
                self.assigned_node_tag = []

            print("Edge mesh @ start span completed")
        self.global_edge_count += 1
        # --------------------------------------------------------------------------------------------
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # second edge construction line
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # get end point of sweep line = point which sweep path intersects end span construction line
        end_point_x = self.long_dim
        # end_point_z = line_func(self.sweep_path.m,self.sweep_path.c,end_point_x)
        end_point_z = self.sweep_path.get_line_function(end_point_x)
        if np.abs(self.skew_2 + self.zeta) < self.skew_threshold[0]:
            # if angle less than threshold, assign nodes of edge member as it is
            current_sweep_nodes = self.end_edge_line.node_list
            for (z_count_int, nodes) in enumerate(current_sweep_nodes):
                x_inc = 0  # end_point_x
                z_inc = 0  # end_point_z
                node_coordinate = [nodes[0] + x_inc, nodes[1], nodes[2] + z_inc]
                self.node_spec.setdefault(
                    self.node_counter,
                    {
                        "tag": self.node_counter,
                        "coordinate": node_coordinate,
                        "x_group": self.global_x_grid_count,
                        "z_group": z_count_int,
                    },
                )

                self.assigned_node_tag.append(self.node_counter)
                self.node_counter += 1
                # if loop assigned more than two nodes, link nodes as a transverse member
                if z_count_int > 0:
                    # run sub procedure to assign
                    # self.__assign_transverse_members(pre_node=self.assigned_node_tag[z_count_int - 1],
                    #                                  cur_node=self.assigned_node_tag[z_count_int])
                    if not self.beam_element_flag:
                        continue
                    if len(self.assigned_node_tag) >= 1:
                        self._assign_edge_trans_members(
                            self.assigned_node_tag[z_count_int - 1],
                            self.assigned_node_tag[z_count_int],
                            self.global_edge_count,
                        )
                        # get and link edge nodes from previous and current as skewed edge member
                        self.edge_node_recorder.setdefault(
                            self.assigned_node_tag[z_count_int - 1],
                            self.global_edge_count,
                        )
                        self.edge_node_recorder.setdefault(
                            self.assigned_node_tag[z_count_int], self.global_edge_count
                        )
                # self.end_connecting_region_nodes = self.assigned_node_tag
                if len(self.assigned_node_tag) == len(self.noz):
                    self.end_connecting_region_nodes = self.assigned_node_tag
            self.global_x_grid_count += 1
        else:
            for z_count, int_point in enumerate(self.end_edge_line.node_list):
                # search point on sweep path line whose normal intersects int_point.
                ref_point_x, ref_point_z = self._search_x_point(
                    int_point, start_point_x
                )
                # record points
                self.sweep_path_points.append(
                    [ref_point_x, self.y_elevation, ref_point_z]
                )
                # find m' of line between intersect int_point and ref point on sweep path
                m_prime, phi = get_slope(
                    [ref_point_x, self.y_elevation, ref_point_z], int_point
                )
                # rotate sweep line such that parallel to m' line
                current_sweep_nodes = self._rotate_sweep_nodes(np.pi / 2 - np.abs(phi))
                # get z group of first node in current_sweep_nodes - for correct assignment in loop
                z_group = self.end_edge_line.get_node_group_z(
                    int_point
                )  # extract from class EdgeConstructionLine
                # check
                # condition
                if 90 + self.skew_2 + self.zeta > 90:
                    sweep_nodes = current_sweep_nodes[0 : (z_count + 1)]
                    z_group_recorder = (
                        list(range(0, z_group + 1)) if z_group != 0 else [0]
                    )
                elif 90 + self.skew_2 + self.zeta < 90:
                    sweep_nodes = current_sweep_nodes[z_count:]
                    z_group_recorder = list(range(z_group, len(current_sweep_nodes)))
                for (z_count_int, nodes) in enumerate(sweep_nodes):
                    x_inc = ref_point_x
                    z_inc = ref_point_z
                    node_coordinate = [nodes[0] + x_inc, nodes[1], nodes[2] + z_inc]
                    self.node_spec.setdefault(
                        self.node_counter,
                        {
                            "tag": self.node_counter,
                            "coordinate": node_coordinate,
                            "x_group": self.global_x_grid_count,
                            "z_group": z_group_recorder[z_count_int],
                        },
                    )

                    self.assigned_node_tag.append(self.node_counter)
                    self.node_counter += 1
                    if not self.beam_element_flag:
                        continue
                    # if loop assigned more than two nodes, link nodes as a transverse member
                    if z_count_int > 0:
                        # run sub procedure to assign
                        self._assign_transverse_members(
                            pre_node=self.assigned_node_tag[z_count_int - 1],
                            cur_node=self.assigned_node_tag[z_count_int],
                        )

                if not self.beam_element_flag:
                    continue

                # if loop is in first step, there is only one column of nodes, skip longitudinal assignment
                if z_count == 0:
                    self.previous_node_tag = self.assigned_node_tag
                if z_count > 0:
                    for pre_node in self.previous_node_tag:
                        for cur_node in self.assigned_node_tag:
                            cur_z_group = self.node_spec[cur_node]["z_group"]
                            prev_z_group = self.node_spec[pre_node]["z_group"]
                            if cur_z_group == prev_z_group:
                                self._assign_longitudinal_members(
                                    pre_node=pre_node,
                                    cur_node=cur_node,
                                    cur_z_group=cur_z_group,
                                )
                                break  # break assign long ele loop (cur node)

                    # if angle is positive (slope negative), edge nodes located at the first element of list
                    if len(self.assigned_node_tag) >= 1:
                        if 90 + self.skew_2 + self.zeta > 90:
                            self._assign_edge_trans_members(
                                self.previous_node_tag[-1],
                                self.assigned_node_tag[-1],
                                self.global_edge_count,
                            )
                            self.edge_node_recorder.setdefault(
                                self.previous_node_tag[-1], self.global_edge_count
                            )
                            self.edge_node_recorder.setdefault(
                                self.assigned_node_tag[-1], self.global_edge_count
                            )
                        elif 90 + self.skew_2 + self.zeta < 90:
                            self._assign_edge_trans_members(
                                self.previous_node_tag[0],
                                self.assigned_node_tag[0],
                                self.global_edge_count,
                            )
                            self.edge_node_recorder.setdefault(
                                self.previous_node_tag[0], self.global_edge_count
                            )
                            self.edge_node_recorder.setdefault(
                                self.assigned_node_tag[0], self.global_edge_count
                            )
                    # update recorder for previous node tag step
                    self.previous_node_tag = self.assigned_node_tag
                # update and reset recorders for next column of sweep nodes
                self.global_x_grid_count += 1
                if len(self.assigned_node_tag) == len(self.noz):
                    self.end_connecting_region_nodes = self.assigned_node_tag
                self.ortho_previous_node_column = self.assigned_node_tag
                self.assigned_node_tag = []
            self.global_edge_count += 1
            print("Edge mesh @ end span completed")
        # --------------------------------------------------------------------------------------------
        self.assigned_node_tag = []  # reset
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # remaining distance mesh with uniform spacing
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        x_first = self.first_connecting_region_nodes[0]
        x_second = self.end_connecting_region_nodes[0]
        # loop each point in self.nox
        cor_fir = self.node_spec[x_first]["coordinate"]
        cor_sec = self.node_spec[x_second]["coordinate"]
        # get x coordinate for uniform region
        self.uniform_region_x = np.linspace(cor_fir[0], cor_sec[0], self.num_trans_beam)

        for z_count, x in enumerate(self.uniform_region_x[1:-1]):
            # get slope, m at current point x
            z = self.sweep_path.get_line_function(x)
            # z = line_func(self.sweep_path.m, self.sweep_path.c, x)
            current_sweep_nodes = self._rotate_sweep_nodes(
                self.zeta / 180 * np.pi
            )  # rotating sweep nodes @ origin
            # if angle less than threshold, assign nodes of edge member as it is
            for (z_count_int, nodes) in enumerate(current_sweep_nodes):
                x_inc = x
                z_inc = z
                node_coordinate = [nodes[0] + x_inc, nodes[1], nodes[2] + z_inc]
                self.node_spec.setdefault(
                    self.node_counter,
                    {
                        "tag": self.node_counter,
                        "coordinate": node_coordinate,
                        "x_group": self.global_x_grid_count,
                        "z_group": z_count_int,
                    },
                )

                self.assigned_node_tag.append(self.node_counter)
                self.node_counter += 1
                if not self.beam_element_flag:
                    continue
                # if loop assigned more than two nodes, link nodes as a transverse member
                if z_count_int > 0:
                    # run sub procedure to assign
                    self._assign_transverse_members(
                        pre_node=self.assigned_node_tag[z_count_int - 1],
                        cur_node=self.assigned_node_tag[z_count_int],
                    )
            if not self.beam_element_flag:
                continue

            if z_count == 0:
                self.previous_node_tag = self.first_connecting_region_nodes
            elif z_count > 0 and z_count != len(self.uniform_region_x[1:-1]) - 1:
                pass
            for pre_node in self.previous_node_tag:
                for cur_node in self.assigned_node_tag:
                    cur_z_group = self.node_spec[cur_node]["z_group"]
                    prev_z_group = self.node_spec[pre_node]["z_group"]
                    if cur_z_group == prev_z_group:
                        self._assign_longitudinal_members(
                            pre_node=pre_node,
                            cur_node=cur_node,
                            cur_z_group=cur_z_group,
                        )
                        break  # break assign long ele loop (cur node)
            # update and reset recorders for next column of sweep nodes
            self.global_x_grid_count += 1
            # update previous node tag recorder
            if z_count != len(self.uniform_region_x[1:-1]) - 1:
                self.previous_node_tag = self.assigned_node_tag
                self.assigned_node_tag = []
            else:
                self.previous_node_tag = self.assigned_node_tag
                self.assigned_node_tag = self.end_connecting_region_nodes

        # Extra step to connect uniform region with nodes along end span edge region
        for pre_node in self.previous_node_tag:
            if not self.beam_element_flag:
                break
            for cur_node in self.assigned_node_tag:
                cur_z_group = self.node_spec[cur_node]["z_group"]
                prev_z_group = self.node_spec[pre_node]["z_group"]
                if cur_z_group == prev_z_group:
                    self._assign_longitudinal_members(
                        pre_node=pre_node, cur_node=cur_node, cur_z_group=cur_z_group
                    )
                    break

    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    def _assign_transverse_members(self, pre_node, cur_node):
        tag = self._get_geo_transform_tag([pre_node, cur_node])
        self.trans_ele.append(
            [self.element_counter, pre_node, cur_node, self.global_x_grid_count, tag]
        )
        self.element_counter += 1

    def _assign_longitudinal_members(self, pre_node, cur_node, cur_z_group):
        tag = self._get_geo_transform_tag([pre_node, cur_node])
        self.long_ele.append(
            [self.element_counter, pre_node, cur_node, cur_z_group, tag]
        )
        self.element_counter += 1

    def _assign_edge_trans_members(
        self, previous_node_tag, assigned_node_tag, edge_counter
    ):
        tag = self._get_geo_transform_tag([previous_node_tag, assigned_node_tag])
        self.edge_span_ele.append(
            [
                self.element_counter,
                previous_node_tag,
                assigned_node_tag,
                edge_counter,
                tag,
            ]
        )
        self.element_counter += 1

    # ------------------------------------------------------------------------------------------
    def _identify_common_z_group(self):
        # dict common element group to z group
        self.common_z_group_element = dict()
        self.common_z_group_element[0] = [
            0,
            len(self.noz) - 1,
        ]  # edge beams top and bottom edge

        # start with case where only 2 grid line in long dir, no exterior and interior beams
        exterior_beam_1_group = []
        exterior_beam_2_group = []
        interior_beam_group = list(
            range(2, len(self.noz) - 2)
        )  # default [] when len(self.noz) < 2
        # if more than 3 grid lines
        if len(self.noz) > 2:
            if len(self.noz) == 3:  # 3 grid lines, 2 edge and 1 interior
                interior_beam_group = [1]  # overwrite interior
            elif len(self.noz) == 4:  # 4 grid line, 2 edge exterior 1 and exterior 2
                exterior_beam_1_group = [1]
                interior_beam_group = []
                exterior_beam_2_group = [len(self.noz) - 2]
            else:
                exterior_beam_1_group = [1]
                exterior_beam_2_group = [len(self.noz) - 2]
        self.common_z_group_element[1] = exterior_beam_1_group  # exterior 1
        self.common_z_group_element[2] = interior_beam_group  # interior
        self.common_z_group_element[3] = exterior_beam_2_group  # exterior 2

    def _identify_member_groups(self):
        """
        Abstracted method handled by either orthogonal_mesh() or skew_mesh() function
        to identify member groups based on node spacings in orthogonal directions.

        :return: Set variable `group_ele_dict` according to
        """

        # dict node tag to width in z direction , and neighbouring node
        self.node_width_z_dict = dict()
        self.node_connect_z_dict = dict()
        for ele in self.long_ele:
            d1 = []  # d for distance
            d2 = []
            p1 = []
            p2 = []
            n1 = [
                trans_ele
                for trans_ele in self.trans_ele
                if trans_ele[1] == ele[1] or trans_ele[2] == ele[1]
            ]
            n2 = [
                trans_ele
                for trans_ele in self.trans_ele
                if trans_ele[1] == ele[2] or trans_ele[2] == ele[2]
            ]
            for item in n1:
                d1.append(
                    [
                        np.abs(a - b)
                        for (a, b) in zip(
                            self.node_spec[item[1]]["coordinate"],
                            self.node_spec[item[2]]["coordinate"],
                        )
                    ]
                )
                if item[1] != ele[1] and item[1] != ele[2]:
                    p1.append(item[1])
                if item[2] != ele[1] and item[2] != ele[2]:
                    p1.append(item[2])

            for item in n2:
                d2.append(
                    [
                        np.abs(a - b)
                        for (a, b) in zip(
                            self.node_spec[item[1]]["coordinate"],
                            self.node_spec[item[2]]["coordinate"],
                        )
                    ]
                )
                if item[1] != ele[1] and item[1] != ele[2]:
                    p2.append(item[1])
                if item[2] != ele[1] and item[2] != ele[2]:
                    p2.append(item[2])
            # list, [ele tag, ele width (left and right)]
            self.node_width_z_dict.setdefault(ele[1], d1)
            self.node_width_z_dict.setdefault(ele[2], d2)
            self.node_connect_z_dict.setdefault(ele[1], p1)
            self.node_connect_z_dict.setdefault(ele[2], p2)

        # dict z to long ele
        self.z_group_to_ele = dict()
        for count, node in enumerate(self.noz):
            self.z_group_to_ele[count] = [
                ele for ele in self.long_ele if ele[3] == count
            ]

        self.global_z_grid_count = max(self.z_group_to_ele.keys()) + 1
        # dict x to trans ele
        self.x_group_to_ele = dict()
        for count in range(0, self.global_x_grid_count):
            self.x_group_to_ele[count] = [
                ele for ele in self.trans_ele if ele[3] == count
            ]
        # dict edge counter to ele
        self.edge_group_to_ele = dict()
        for count in range(0, self.global_edge_count + 1):
            self.edge_group_to_ele[count] = [
                ele for ele in self.edge_span_ele if ele[3] == count
            ]
        # dict node tag to width in x direction
        self.node_width_x_dict = dict()
        self.node_connect_x_dict = dict()
        for ele in self.trans_ele:
            d1 = []
            d2 = []
            p1 = []
            p2 = []
            n1 = [
                long_ele
                for long_ele in self.long_ele
                if long_ele[1] == ele[1] or long_ele[2] == ele[1]
            ]
            n2 = [
                long_ele
                for long_ele in self.long_ele
                if long_ele[1] == ele[2] or long_ele[2] == ele[2]
            ]
            for item in n1:
                d1.append(
                    [
                        np.abs(a - b)
                        for (a, b) in zip(
                            self.node_spec[item[1]]["coordinate"],
                            self.node_spec[item[2]]["coordinate"],
                        )
                    ]
                )
                if item[1] != ele[1] and item[1] != ele[2]:
                    p1.append(item[1])
                if item[2] != ele[1] and item[2] != ele[2]:
                    p1.append(item[2])
            for item in n2:
                d2.append(
                    [
                        np.abs(a - b)
                        for (a, b) in zip(
                            self.node_spec[item[1]]["coordinate"],
                            self.node_spec[item[2]]["coordinate"],
                        )
                    ]
                )
                if item[1] != ele[1] and item[1] != ele[2]:
                    p2.append(item[1])
                if item[2] != ele[1] and item[2] != ele[2]:
                    p2.append(item[2])
            # list, [ele tag, ele width (left and right)]
            self.node_width_x_dict.setdefault(ele[1], d1)
            self.node_width_x_dict.setdefault(ele[2], d2)
            self.node_connect_x_dict.setdefault(ele[1], p1)
            self.node_connect_x_dict.setdefault(ele[2], p2)

        for ele in self.edge_span_ele:
            d1 = []
            d2 = []
            p1 = []
            p2 = []
            n1 = [
                long_ele
                for long_ele in self.long_ele
                if long_ele[1] == ele[1] or long_ele[2] == ele[1]
            ]
            n2 = [
                long_ele
                for long_ele in self.long_ele
                if long_ele[1] == ele[2] or long_ele[2] == ele[2]
            ]
            for item in n1:
                d1.append(
                    [
                        np.abs(a - b)
                        for (a, b) in zip(
                            self.node_spec[item[1]]["coordinate"],
                            self.node_spec[item[2]]["coordinate"],
                        )
                    ]
                )
                if item[1] != ele[1] and item[1] != ele[2]:
                    p1.append(item[1])
                if item[2] != ele[1] and item[2] != ele[2]:
                    p1.append(item[2])
            for item in n2:
                d2.append(
                    [
                        np.abs(a - b)
                        for (a, b) in zip(
                            self.node_spec[item[1]]["coordinate"],
                            self.node_spec[item[2]]["coordinate"],
                        )
                    ]
                )
                if item[1] != ele[1] and item[1] != ele[2]:
                    p2.append(item[1])
                if item[2] != ele[1] and item[2] != ele[2]:
                    p2.append(item[2])
            # list, [ele tag, ele width (left and right)]
            self.node_width_x_dict.setdefault(ele[1], d1)
            self.node_width_x_dict.setdefault(ele[2], d2)
            self.node_connect_x_dict.setdefault(ele[1], p1)
            self.node_connect_x_dict.setdefault(ele[2], p2)
        # create self.grid_number_dict, dict key = grid number, val = long and trans ele in grid
        self.grid_number_dict = dict()
        counter = 0
        for node_tag in self.node_spec.keys():
            # get the surrounding nodes
            x_vicinity_nodes = self.node_connect_x_dict.get(node_tag, [])
            z_vicinity_nodes = self.node_connect_z_dict.get(node_tag, [])
            for x_node in x_vicinity_nodes:
                xg = self.node_spec[x_node]["x_group"]
                for z_node in z_vicinity_nodes:
                    zg = self.node_spec[z_node]["z_group"]
                    # find the 3rd bounding node
                    n3 = [
                        n["tag"]
                        for n in self.node_spec.values()
                        if n["x_group"] == xg and n["z_group"] == zg
                    ]
                    if n3:
                        n3 = n3[0]
                        if not any(
                            [
                                node_tag in d
                                and x_node in d
                                and z_node in d
                                and n3 in d
                                for d in self.grid_number_dict.values()
                            ]
                        ):
                            self.grid_number_dict.setdefault(
                                counter, [node_tag, x_node, n3, z_node]
                            )
                            counter += 1
                    else:  # list is empty
                        if not any(
                            [
                                node_tag in d and x_node in d and z_node in d
                                for d in self.grid_number_dict.values()
                            ]
                        ):
                            self.grid_number_dict.setdefault(
                                counter, [node_tag, x_node, n3, z_node]
                            )
                            counter += 1

        # dict of grid number return vicinity grid number in a subdict {'x-1': 'x+1', 'z-1' , 'z+1'}
        self.grid_vicinity_dict = dict()
        for k, grid in self.grid_number_dict.items():
            current_x_group = []
            current_z_group = []
            current_x = []
            current_z = []

            grid_number_record = []
            if [] in grid:
                grid.remove([])
            for node in grid:
                grid_number_record += [
                    i
                    for i, x in enumerate(
                        [node in n for n in self.grid_number_dict.values()]
                    )
                    if x
                ]
                current_x_group.append(self.node_spec[node]["x_group"])
                current_z_group.append(self.node_spec[node]["z_group"])
                current_x.append(self.node_spec[node]["coordinate"][0])
                current_z.append(self.node_spec[node]["coordinate"][2])
            current_x_group = list(np.unique(current_x_group))
            current_z_group = list(np.unique(current_z_group))
            current_x = list(np.unique(current_x))
            current_z = list(np.unique(current_z))
            grid_number_record = np.unique(grid_number_record)
            # loop to characterize the grid for current
            subdict = {}
            for neighbour in grid_number_record:
                if neighbour == k:  # identical , current grid
                    continue
                x_group = []  # initialize variables
                x_coor = []
                z_group = []
                z_coor = []
                # loop each node in the vicintiy grids
                for nodes in self.grid_number_dict[neighbour]:
                    if not nodes:
                        continue
                    x_group.append(self.node_spec[nodes]["x_group"])
                    z_group.append(self.node_spec[nodes]["z_group"])
                    x_coor.append(self.node_spec[nodes]["coordinate"][0])
                    z_coor.append(self.node_spec[nodes]["coordinate"][2])
                x_group = list(np.unique(x_group))
                z_group = list(np.unique(z_group))
                x_coor = list(np.unique(x_coor))
                z_coor = list(np.unique(z_coor))
                # if x groups are identical, neighbour grid is either top or bottom of the element
                if all(a in current_x_group for a in x_group):
                    # compare z max
                    if max(z_coor) > max(current_z):
                        subdict["top"] = neighbour
                    else:
                        subdict["bottom"] = neighbour
                # if x groups are identical, neighbour grid is either left or right of the element
                if all(a in current_z_group for a in z_group):
                    if max(x_coor) > max(current_x):
                        subdict["right"] = neighbour
                    else:
                        subdict["left"] = neighbour
            self.grid_vicinity_dict.setdefault(k, subdict)

    def _get_geo_transform_tag(self, ele_nodes, offset=None):
        # offset is not used in version 0.1.0
        if offset is None:
            offset = []  #
        # function called for each element, assign
        node_i = self.node_spec[ele_nodes[0]]["coordinate"]
        node_j = self.node_spec[ele_nodes[1]]["coordinate"]
        vxz = self._get_vector_xz(node_i, node_j)
        vxz = [np.round(num, decimals=self.decimal_lim) for num in vxz]
        tag_value = self.transform_dict.setdefault(
            repr(vxz) + "|" + repr(offset), self.transform_counter + 1
        )
        if tag_value > self.transform_counter:
            self.transform_counter = tag_value
        return tag_value

    def _check_skew(self, edge_skew_angle, zeta):
        # zeta in DEGREES
        # if mesh type is beyond default allowance threshold of 11 degree and 30 degree, return exception
        if np.abs(edge_skew_angle - zeta) <= self.skew_threshold[0] and self.orthogonal:
            # return error
            raise Exception(
                "Skew angle too small for orthogonal, minimum edge skew angle for an orthogonal mesh is {}".format(
                    self.skew_threshold[0]
                )
            )
        elif (
            np.abs(edge_skew_angle - zeta) >= self.skew_threshold[1]
            and not self.orthogonal
        ):
            self.orthogonal = True
            raise Exception(
                "Skew angle too large for Oblique mesh, maximum edge skew angle for Oblique mesh is {}".format(
                    (self.skew_threshold[1])
                )
            )
            # raise Exception('Oblique mesh not allowed for angle greater than {}'.format(self.skew_threshold[1]))

    # ------------------------------------------------------------------------------------------
    @staticmethod
    def _get_vector_xz(node_i, node_j):
        """
        Encapsulated function to identify a vector parallel to the plane of local x and z axis of the element. The
        vector is required for geomTransf() command
        - see geomTransf_.

        .. _geomTransf: https://openseespydoc.readthedocs.io/en/latest/src/geomTransf.html

        """
        # Function to calculate vector xz used for geometric transformation of local section properties
        # return: vector parallel to plane xz of member (see geotransform Opensees) for skew members (member tag 5)

        # vector rotate 90 deg clockwise (x,y) -> (y,-x)
        # [breadth width] is a vector parallel to skew
        xi = node_j[0] - node_i[0]
        zi = node_j[2] - node_i[2]
        x = zi
        z = -xi
        # normalize vector
        length = np.sqrt(x**2 + z**2)
        x1 = x / length

        z1 = z / length
        return [x1, 0, z1]  # here y axis is normal to model plane

    def _rotate_sweep_nodes(self, zeta):
        sweep_nodes_x = [0] * len(
            self.noz
        )  # line is orthogonal at the start of sweeping path
        # rotate for inclination at origin
        sweep_nodes_x = [
            x * np.cos(zeta) - y * np.sin(zeta) for x, y in zip(sweep_nodes_x, self.noz)
        ]
        sweep_nodes_z = [
            y * np.cos(zeta) + x * np.sin(zeta) for x, y in zip(sweep_nodes_x, self.noz)
        ]

        sweeping_nodes = [
            [x + self.mesh_origin[0], y + self.mesh_origin[1], z + self.mesh_origin[2]]
            for x, y, z in zip(
                (sweep_nodes_x), [self.y_elevation] * len(self.noz), sweep_nodes_z
            )
        ]

        return sweeping_nodes

    def _search_x_point(self, int_point, start_point_y=0, line_function=None):
        start_point_x = int_point[0]
        min_found = False
        max_loop = 1000
        loop_counter = 0
        z0 = None
        inc = self.search_x_inc
        convergence_check = []
        bounds = []
        while not min_found:
            z0 = self.sweep_path.get_line_function(start_point_x)
            z_ub = self.sweep_path.get_line_function(start_point_x + inc)
            z_lb = self.sweep_path.get_line_function(start_point_x - inc)
            d0 = find_min_x_dist(
                [int_point], [[start_point_x, self.y_elevation, z0]]
            ).tolist()

            d_ub = find_min_x_dist(
                [int_point], [[start_point_x + inc, self.y_elevation, z_ub]]
            ).tolist()

            d_lb = find_min_x_dist(
                [int_point], [[start_point_x - inc, self.y_elevation, z_lb]]
            ).tolist()

            if d_lb > d0 and d_ub > d0:
                min_found = True
            elif d_lb < d0 and d_ub > d0:
                start_point_x = start_point_x - inc
            elif d_lb > d0 and d_ub < d0:
                start_point_x = start_point_x + inc

            loop_counter += 1
            if loop_counter > max_loop:
                break

        return start_point_x, z0


class EdgeControlLine:
    """
    Main class for edge control points. This class holds information for node meshing points of model edges - start and
    end spans. This class is used in BeamMesh class.
    """

    def __init__(
        self,
        edge_ref_point,
        width_z,
        edge_width_a,
        edge_width_b,
        edge_angle,
        num_long_beam,
        model_plane_y,
        feature="standard",
        ext_to_int_a=None,
        ext_to_int_b=None,
        **kwargs
    ):

        # distance between interior beam and exterior beam
        self.ext_to_int_a = ext_to_int_a
        self.ext_to_int_b = ext_to_int_b
        # set variables
        self.edge_ref_point = edge_ref_point
        self.width_z = width_z
        self.edge_width_a = edge_width_a
        self.edge_width_b = edge_width_b
        self.num_long_beam = num_long_beam
        self.edge_angle = edge_angle
        self.feature = feature

        # for shell
        self.z_group_master_pair_list = []
        self.node_z_pair_list_value = []
        # counter
        self.customize = kwargs.get("custom", None)  # get the list
        if self.customize and not isinstance(self.customize, list):
            raise Exception(
                "Invalid custom control point format: Hint - accepts list of float or int"
            )

        # calculations
        # TODO TEST
        # array containing z coordinate of edge construction line
        last_girder = self.width_z - self.edge_width_b  # coord of exterior main beam 2

        last_interior = (
            last_girder - self.ext_to_int_b if self.ext_to_int_b is not None else None
        )
        first_interior = (
            self.edge_width_a + self.ext_to_int_a
            if self.ext_to_int_a is not None
            else None
        )

        # check cases of customize edge control points
        if (
            not first_interior and not last_interior
        ):  # no custom dist between interior and exterior
            nox_girder = np.linspace(
                start=self.edge_width_a, stop=last_girder, num=self.num_long_beam - 2
            )
        elif first_interior and not last_interior:
            nox_girder = np.hstack(
                (
                    edge_width_a,
                    np.linspace(
                        start=first_interior,
                        stop=last_girder,
                        num=self.num_long_beam - 2 - 1,
                    ),
                )
            )
        elif not first_interior and last_interior:
            nox_girder = np.hstack(
                (
                    np.linspace(
                        start=self.edge_width_a,
                        stop=last_interior,
                        num=self.num_long_beam - 2 - 1,
                    ),
                    last_girder,
                )
            )

        else:  # both have custom interior ext distance
            nox_girder = np.linspace(
                start=first_interior, stop=last_interior, num=self.num_long_beam - 4
            )
            nox_girder = np.hstack((edge_width_a, nox_girder))
            nox_girder = np.hstack((nox_girder, last_girder))

        # create self.noz points
        self._create_trans_grid(nox_girder=nox_girder)
        # if self.feature == "standard":
        #     self.noz = np.hstack((np.hstack((0, nox_girder)), self.width_z))
        # elif self.feature == "shell_link":

        # if negative angle, create edge_node_x based on negative angle algorithm, else positive angle algorithm
        if self.edge_angle <= 0:
            edge_node_x = [
                -(z * np.tan(self.edge_angle / 180 * np.pi)) for z in self.noz
            ]  # rotate z by edge angle
            self.node_list = [
                [
                    x + self.edge_ref_point[0],
                    y + self.edge_ref_point[1],
                    z + self.edge_ref_point[2],
                ]
                for x, y, z in zip(
                    edge_node_x, [model_plane_y] * len(self.noz), self.noz
                )
            ]
        else:
            edge_node_x = [
                -(z * np.tan(self.edge_angle / 180 * np.pi)) for z in self.noz
            ]
            self.node_list = [
                [
                    x + self.edge_ref_point[0],
                    y + self.edge_ref_point[1],
                    z + self.edge_ref_point[2],
                ]
                for x, y, z in zip(
                    edge_node_x, [model_plane_y] * len(self.noz), self.noz
                )
            ]

        self.z_group = list(range(0, len(self.noz)))

        self.slope = (
            -1 / np.tan(self.edge_angle / 180 * np.pi) if self.edge_angle != 0 else None
        )
        self.c = (
            get_y_intcp(self.slope, self.edge_ref_point[0], self.edge_ref_point[2])
            if self.edge_angle != 0
            else None
        )

    def get_node_group_z(self, coordinate):
        # return list of zgroup
        group = self.node_list.index(coordinate)
        return group

    def _create_trans_grid(self, nox_girder):
        self.noz = np.hstack((np.hstack((0, nox_girder)), self.width_z))


class ShellEdgeControlLine(EdgeControlLine):
    """
    Child class of EdgeControlLine. This class is used by ShellMesh class
    """

    def __init__(
        self,
        edge_ref_point,
        width_z,
        edge_width_a,
        edge_width_b,
        edge_angle,
        num_long_beam,
        model_plane_y,
        feature="standard",
        ext_to_int_a=None,
        ext_to_int_b=None,
        **kwargs
    ):
        # get properties specific to shell mesh
        self.beam_width = kwargs.get(
            "beam_width", None
        )  # information from kwargs of Shellmodel class
        self.max_mesh_size_z = kwargs.get(
            "max_mesh_size_z"
        )  # information from kwargs of Shellmodel class
        self.max_mesh_size_x = kwargs.get(
            "max_mesh_size_x"
        )  # information from kwargs of Shellmodel class
        super().__init__(
            edge_ref_point,
            width_z,
            edge_width_a,
            edge_width_b,
            edge_angle,
            num_long_beam,
            model_plane_y,
            feature,
            ext_to_int_a,
            ext_to_int_b,
            **kwargs
        )

    # function specific to shell edge line
    def _get_shell_z_group_pair(self):
        for node_z_pair in self.node_z_pair_list_value:
            # get first and second z group of paired z group corresponding to links to offset line element
            list_index = [
                self.noz.index(node_z_pair[0]),
                self.noz.index(node_z_pair[1]),
            ]
            self.z_group_master_pair_list.append(list_index)

    def _create_trans_grid(self, nox_girder):
        z_spacing = self.beam_width / 2
        mesh_z_spacing = self.max_mesh_size_z
        self.beam_position = np.hstack(
            (np.hstack((0, nox_girder)), self.width_z)
        )  # default noz representing beam position
        shell_noz = [self.edge_ref_point[2]]  # first and last node z
        for beam_node_z in self.beam_position[1:-1]:
            local_list = (
                []
            )  # create local list of control points (local to each beam group)
            # create external control points between beam groups
            num_points_external = math.ceil(
                (beam_node_z - z_spacing - shell_noz[-1]) / mesh_z_spacing
            )
            local_list += np.linspace(
                shell_noz[-1], beam_node_z - z_spacing, num_points_external + 1
            ).tolist()
            # local_list += np.linspace(shell_noz[-1], beam_node_z - z_spacing, 2).tolist()  # external
            # create internal control points within the beam group
            num_points_internal = math.ceil(z_spacing * 2 / mesh_z_spacing)
            local_list += np.linspace(
                beam_node_z - z_spacing,
                beam_node_z + z_spacing,
                num_points_internal + 1,
            ).tolist()[1:]
            self.node_z_pair_list_value.append(
                [beam_node_z - z_spacing, beam_node_z + z_spacing]
            )
            shell_noz += local_list[1:]
        # create points between exterior beam to outer edge beam
        num_points_external = math.ceil((self.width_z - shell_noz[-1]) / mesh_z_spacing)
        shell_noz += np.linspace(
            shell_noz[-1], self.width_z, num_points_external + 1
        ).tolist()[1:]
        shell_noz.sort()
        self.noz = shell_noz  #
        self._get_shell_z_group_pair()


class SweepPath:
    """
    Main class for sweep path. Sweep path is assigned to an EdgeControlLine class in order to create mesh of nodes
    across its path. The constuctor is handled by Mesh classes ( either base or concrete classes)
    """

    def __init__(self, pt1: Point, pt2: Point, pt3: Point = None):
        """

        :param pt1: Namedtuple Point of first coordinate
        :param pt2: Namedtuple Point of second coordinate
        :param pt3: Namedtuple Point of third coordinate
        """
        self.pt1 = pt1  # default first
        self.pt2 = pt2  # default second / last for linear line
        self.pt3 = pt3  # default mid point of a curved line defined using 3 points
        self.decimal_lim = 4
        self.curve_path = False
        # return variables
        self.zeta = None
        self.m = None
        self.c = 0  # Default:0 , sweep path intersects origin

    def get_sweep_line_properties(self):
        if self.pt3 is not None:
            try:
                self.d = find_circle(
                    x1=0,
                    y1=0,
                    x2=self.pt2.x,
                    y2=self.pt2.z,
                    x3=self.pt3.x,
                    y3=self.pt3.z,
                )
                self.curve_path = True
            except ZeroDivisionError:
                return Exception(
                    "Zero div error. Point 3 not valid to construct curve line"
                )
            # procedure
            # get tangent at origin
            self.zeta = 0
            # get tangent at end of curve line (intersect with second construction line)

        else:
            # construct straight line sweep path instead
            self.d = None
            # procedure to identify straight line segment pinpointing length of grillage
            points = [(self.pt1.x, self.pt1.z), (self.pt2.x, self.pt2.z)]
            x_coords, y_coords = zip(*points)
            A = np.vstack([x_coords, np.ones(len(x_coords))]).T
            m, c = np.linalg.lstsq(A, y_coords, rcond=None)[0]
            self.m = round(m, self.decimal_lim)
            # self.c = 0  # default 0  to avoid arithmetic error
            zeta = np.arctan(
                m
            )  # initial angle of inclination of sweep line about mesh origin
            self.zeta = zeta / np.pi * 180  # rad to degrees
            self.eta_angle = self.zeta

        return self.zeta, self.m, self.c

    def get_line_function(self, x):
        if not self.curve_path:
            # straight line
            return line_func(self.m, self.c, x)
        else:
            # TODO for curve line
            pass


# ---------------------------------------------------------------------------------------------------------------------
# concrete classes of Mesh
class BeamMesh(Mesh):
    """
    Concrete class for Mesh class. This is the default Mesh class for Beam grillage
    """

    def __init__(
        self,
        long_dim,
        width,
        trans_dim,
        edge_dist_a,
        edge_dist_b,
        num_trans_beam,
        num_long_beam,
        skew_1,
        skew_2,
        ext_to_int_a,
        ext_to_int_b,
        **kwargs
    ):
        """
        Subclass for Mesh with beam. This class creates elements where:
        - nodes of longitudinal beams are offset in global y direction
        - nodes of transverse slab are offset in direction of element axial direction

        :param long_dim:
        :param width:
        :param trans_dim:
        :param edge_dist_a:
        :param edge_dist_b:
        :param num_trans_beam:
        :param num_long_beam:
        :param skew_1:
        :param skew_2:
        :param ext_to_int_a:
        :param ext_to_int_b:
        """
        # instantiate variables specific for current mesh subclass

        # super init to create mesh of grillage @ model plane = 0 using base class init
        super().__init__(
            long_dim,
            width,
            trans_dim,
            edge_dist_a,
            edge_dist_b,
            num_trans_beam,
            num_long_beam,
            skew_1,
            skew_2,
            ext_to_int_a,
            ext_to_int_b,
            **kwargs
        )


class BeamLinkMesh(Mesh):
    """
    Concrete class for Mesh class. This Mesh class is for model type 2: Beam grillage with rigid links and offsets
    """

    def __init__(
        self,
        long_dim,
        width,
        trans_dim,
        edge_dist_a,
        edge_dist_b,
        num_trans_beam,
        num_long_beam,
        skew_1,
        skew_2,
        ext_to_int_a,
        ext_to_int_b,
        **kwargs
    ):
        """
        Subclass for Mesh with beam. This class creates elements where:
        - nodes of longitudinal beams are offset in global y direction
        - nodes of transverse slab are offset in direction of element axial direction

        :param long_dim:
        :param width:
        :param trans_dim:
        :param edge_dist_a:
        :param edge_dist_b:
        :param num_trans_beam:
        :param num_long_beam:
        :param skew_1:
        :param skew_2:
        :param ext_to_int_a:
        :param ext_to_int_b:
        """
        # instantiate variables specific for beam link model
        self.beam_width = kwargs.get("beam_width", None)
        self.web_thick = kwargs.get("web_thick", None)
        self.centroid_dist_y = kwargs.get("centroid_dist_y", 0)
        if any([self.beam_width is None and self.web_thick is None]):
            self.offset_z_dist = 0
        else:
            self.offset_z_dist = self.beam_width / 2 - self.web_thick / 2

        # super init to create mesh of grillage @ model plane = 0 using base class init
        super().__init__(
            long_dim,
            width,
            trans_dim,
            edge_dist_a,
            edge_dist_b,
            num_trans_beam,
            num_long_beam,
            skew_1,
            skew_2,
            ext_to_int_a,
            ext_to_int_b,
            **kwargs
        )

    def _get_geo_transform_tag(self, ele_nodes, offset=None):
        """
        overwrite base class method to get geom transf of beam element
        """
        global_offset = []  #
        local_offset = []  #
        # function called for each element, assign
        node_i = self.node_spec[ele_nodes[0]]["coordinate"]
        node_j = self.node_spec[ele_nodes[1]]["coordinate"]
        def_l = find_min_x_dist([node_i], [node_j]).tolist()[0][
            0
        ]  # distance between i and j, returned as 2D array
        mid_node = [
            (node_i[0] + node_j[0]) / 2,
            (node_i[1] + node_j[1]) / 2,
            (node_i[2] + node_j[2]) / 2,
        ]
        vxz = self._get_vector_xz(node_i, node_j)

        # determine local offset of node based on element groups, get global offset for node i and j of geomtransf
        # if element is a longitudinal, set global y offset (for longitudinal beam)
        if (
            self.node_spec[ele_nodes[1]]["z_group"]
            == self.node_spec[ele_nodes[0]]["z_group"]
        ):
            # check if not an edge beam
            if self.node_spec[ele_nodes[1]]["z_group"] != 0 or self.node_spec[
                ele_nodes[1]
            ]["z_group"] != len(self.noz):
                local_offset = [
                    0,
                    -self.centroid_dist_y,
                    0,
                ]  # shift beam element by global y

        # if element is a transverse member, calculate local offset based on member orientation
        elif (
            self.node_spec[ele_nodes[1]]["x_group"]
            == self.node_spec[ele_nodes[0]]["x_group"]
        ):
            # calculate local offset
            offset_z = self.offset_z_dist  # z == cos
            offset_x = (
                (node_i[0] + node_j[0]) / (node_i[2] + node_j[2]) * self.offset_z_dist
            )
            local_offset = [offset_x, self.y_elevation, offset_z]
        if local_offset:
            if (
                find_min_x_dist(
                    [[a - b for a, b in zip(node_i, local_offset)]], [node_j]
                ).tolist()[0][0]
                < def_l
            ):

                global_offset_i = [a - b for a, b in zip(node_i, local_offset)]
                global_offset_j = [a + b for a, b in zip(node_j, local_offset)]
            else:  # reciprocal , node i has to minus local offset

                global_offset_i = [a + b for a, b in zip(node_i, local_offset)]
                global_offset_j = [a - b for a, b in zip(node_j, local_offset)]
            global_offset = [global_offset_i, global_offset_j]
        vxz = [np.round(num, decimals=self.decimal_lim) for num in vxz]
        tag_value = self.transform_dict.setdefault(
            repr(vxz) + "|" + repr(global_offset), self.transform_counter + 1
        )
        if tag_value > self.transform_counter:
            self.transform_counter = tag_value
        return tag_value


class ShellLinkMesh(Mesh):
    """
    Concrete class for Mesh class. This Mesh class is for model type 3: Shell hybrid model with rigid links
    """

    def __init__(
        self,
        long_dim,
        width,
        trans_dim,
        edge_dist_a,
        edge_dist_b,
        num_trans_beam,
        num_long_beam,
        skew_1,
        skew_2,
        ext_to_int_a,
        ext_to_int_b,
        link_type="beam",
        **kwargs
    ):
        """
        Subclass for mesh with offset beam members linked to grillage consisting of shell elements

        :param long_dim:
        :param width:
        :param trans_dim:
        :param edge_dist_a:
        :param edge_dist_b:
        :param num_trans_beam:
        :param num_long_beam:
        :param skew_1:
        :param skew_2:
        :param ext_to_int_a:
        :param ext_to_int_b:
        """
        # instantiate variables specific for shell mesh subclass
        self.long_ele_offset = []
        self.link_str_list = []
        self.link_type = link_type
        self.link_dict = dict()  # key is node tag c, val is list of master node r
        self.offset_node_group_dict = (
            dict()
        )  # key is node tag of offset node, val is beam group
        self.edge_support_nodes = dict()
        # variables for support - the ends of beam offset elements
        self.pinned_node_group = 0
        self.roller_node_group = 1
        # get variables from keyword arguments
        self.y_offset = kwargs.get("offset_beam_y_dist", 0.449)  # Here default values
        self.beam_width = kwargs.get("beam_width", 0.445)  # Here default values
        self.max_mesh_size_z = kwargs.get("max_mesh_size_z", 1)  # Here default values
        self.max_mesh_size_x = kwargs.get("max_mesh_size_x", 1)  # Here default values
        # variables to store assignment counters after meshing of main model plane grid y = 0
        self.x_grid_to_x_dict = (
            dict()
        )  # key is x value (m), value is x grid number (for offset nodes)
        self.z_grid_to_z_dict = (
            dict()
        )  # key is z value (m), value is z grid number (for offset nodes)

        # use meshing procedure of base mesh class
        super().__init__(
            long_dim,
            width,
            trans_dim,
            edge_dist_a,
            edge_dist_b,
            num_trans_beam,
            num_long_beam,
            skew_1,
            skew_2,
            ext_to_int_a,
            ext_to_int_b,
            **kwargs
        )

        # meshing procedure to create beam offset element and tie it with rigid links to master nodes of model plane y=0
        self._create_offset_beam_element()

        # overwrite procedure to identify
        self._identify_common_z_group()
        # base class stores node groups as self.model_plane_z_groups, here for offset elements store as new variable
        self.offset_z_groups = [
            a
            for a in list(self.z_group_to_ele.keys())
            if a not in self.model_plane_z_groups
        ]

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which are overwritten of that from base class to for specific shell type model
    def create_control_points(self, **kwargs):

        return ShellEdgeControlLine(**kwargs)

    # add groupings of offset beam elements

    # ----------------------------------------------------------------------------------------------------------------
    # sub procedures specific to shell meshes
    def _create_offset_beam_element(self):

        # sub procedure function to create beam elements based on offset nodes
        self._create_offset_nodes()

        # create offset elements commands
        for cNode, rNode_list in self.link_dict.items():
            for rNode in rNode_list:
                self._create_link_element(rNode=rNode, cNode=cNode)

        # loop each beam group and create beam elements from these offset nodes
        for beam_group in range(0, len(self.start_edge_line.z_group_master_pair_list)):
            offset_node_tag = [
                k for k, v in self.offset_node_group_dict.items() if v == beam_group
            ]  # key is offset node
            # sort offset node tag based on x longitudinal position
            x_coord_list = [
                self.node_spec[tag]["coordinate"][0] for tag in offset_node_tag
            ]
            sorted_offset_tag = [
                x for _, x in sorted(zip(x_coord_list, offset_node_tag))
            ]
            # store first and last node tag as supports
            self.edge_support_nodes.setdefault(
                sorted_offset_tag[0], self.pinned_node_group
            )  #
            self.edge_support_nodes.setdefault(
                sorted_offset_tag[-1], self.roller_node_group
            )
            # assign long beam element between two nodes
            for ind, node_tag in enumerate(sorted_offset_tag[:-1]):
                n1 = node_tag
                n2 = sorted_offset_tag[ind + 1]
                transf_tag = self._get_geo_transform_tag(ele_nodes=[n1, n2])
                self.long_ele.append(
                    [
                        self.element_counter,
                        n1,
                        n2,
                        beam_group + self.global_z_grid_count,
                        transf_tag,
                    ]
                )
                self.element_counter += 1

            # add to grouping dict data
            self.z_group_to_ele[beam_group + self.global_z_grid_count] = [
                ele
                for ele in self.long_ele
                if ele[3] == beam_group + self.global_z_grid_count
            ]

    def _create_offset_nodes(self):
        # sub procedure function
        x_count = "offset_beam_x"  # proxy
        z_count = "offset_beam_group_z{}"  # proxy
        # get groups of node master pairs
        z_pair = self.start_edge_line.z_group_master_pair_list
        # loop each z pair
        # loop each x group
        for x_group in range(0, self.global_x_grid_count):
            for beam_group, z_pair_group in enumerate(z_pair):
                n1 = [
                    key
                    for key, n in self.node_spec.items()
                    if n["x_group"] == x_group and n["z_group"] == z_pair_group[0]
                ]
                n2 = [
                    key
                    for key, n in self.node_spec.items()
                    if n["x_group"] == x_group and n["z_group"] == z_pair_group[1]
                ]

                if not len(n1) == 1 or not len(n2) == 1:
                    continue
                n1_coord = self.node_spec[n1[0]]["coordinate"]
                n2_coord = self.node_spec[n2[0]]["coordinate"]

                # create offset node
                mid_pt = [(a + b) / 2 for a, b in zip(n1_coord, n2_coord)]
                node_coordinate = [mid_pt[0], mid_pt[1] + self.y_offset, mid_pt[2]]
                self.node_spec.setdefault(
                    self.node_counter,
                    {
                        "tag": self.node_counter,
                        "coordinate": node_coordinate,
                        "x_group": x_count,
                        "z_group": z_count.format(beam_group),
                    },
                )

                # store offset node rigid details
                master_node_list = [n1[0], n2[0]]  # list of list
                self.link_dict.setdefault(self.node_counter, master_node_list)

                # store node - beam group detail
                # beam_group = [ind for ind, i in enumerate([self.node_spec in z for z in z_pair]) if i][0]  # numbering of beam group
                self.offset_node_group_dict.setdefault(
                    self.node_counter, beam_group
                )  # c node is key, group num is val
                self.node_counter += 1

        # generate for edge nodes - only for orthogonal mesh
        if self.orthogonal:
            for edge_group in range(0, self.global_edge_count):
                for beam_group, z_pair_group in enumerate(z_pair):
                    n1 = [
                        key
                        for key, n in self.node_spec.items()
                        if key in self.edge_node_recorder.keys()
                        and n["z_group"] == z_pair_group[0]
                    ]
                    n2 = [
                        key
                        for key, n in self.node_spec.items()
                        if key in self.edge_node_recorder.keys()
                        and n["z_group"] == z_pair_group[1]
                    ]

                    if not len(n1) == 1 or not len(n2) == 1:
                        continue
                    n1_coord = self.node_spec[n1[0]]["coordinate"]
                    n2_coord = self.node_spec[n2[0]]["coordinate"]

                    # create offset node
                    mid_pt = [(a + b) / 2 for a, b in zip(n1_coord, n2_coord)]
                    node_coordinate = [mid_pt[0], mid_pt[1] + self.y_offset, mid_pt[2]]
                    self.node_spec.setdefault(
                        self.node_counter,
                        {
                            "tag": self.node_counter,
                            "coordinate": node_coordinate,
                            "x_group": x_count,
                            "z_group": z_count.format(beam_group),
                        },
                    )

                    # store offset node rigid details
                    master_node_list = [n1[0], n2[0]]  # list of list
                    self.link_dict.setdefault(self.node_counter, master_node_list)

                    # store node - beam group detail
                    # beam_group = [ind for ind, i in enumerate([self.node_spec in z for z in z_pair]) if i][0]  # numbering of beam group
                    self.offset_node_group_dict.setdefault(
                        self.node_counter, beam_group
                    )  # c node is key, group num is val
                    self.node_counter += 1

    def _create_link_element(self, rNode, cNode):
        # sub procedure function
        # user mp constraint object
        # function to create ops rigid link command and store to variable

        link_str = 'ops.rigidLink("{linktype}",{rNodetag},{cNodetag})\n'.format(
            linktype=self.link_type, rNodetag=cNode, cNodetag=rNode
        )

        self.link_str_list.append(link_str)


# -----------------------------------------------------------------------------------------------------------------
# concrete classes for mesh elements
