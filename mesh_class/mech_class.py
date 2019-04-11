from math import atan2, sin, cos, pi

import numpy as np

xyz_idx = {'x': 0, 'y': 1, 'z': 2}


class Node:
    def __init__(self, label, x, y, z):
        self.label = label
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return str(self.label)


class Element:
    def __init__(self, label, nodes, element_type):
        self.id = label
        self.element_type = element_type

        if element_type[1] == '3':
            dim = 3
        else:
            dim = 2
        e_nodes = []
        for i in range(dim - 1):
            if element_type[3] == '8':
                plane_nodes = nodes[4*i:4*(i + 1)]

            elif element_type[3] == '6':
                plane_nodes = nodes[3*i:3*(i + 1)]
            else:
                raise NotImplementedError("Mesh class currently doesnt support " + element_type)

            x0 = sum([node.x for node in plane_nodes])/len(plane_nodes)
            y0 = sum([node.y for node in plane_nodes])/len(plane_nodes)
            e_nodes += sorted(plane_nodes, key=lambda n: atan2(n.y - y0, n.x - x0))
        self.nodes = e_nodes


class MeshClass:
    def __init__(self):
        self.nodes = {}
        self.node_sets = {}
        self.element_sets = {}
        self.elements = {}
        self.node_counter = 1
        self.element_counter = 1

    def create_node(self, x, y, z, node_set=None, label=None):
        if label is None:
            label = self.node_counter
            self.node_counter += 1
        else:
            self.node_counter = label + 1
        n = Node(label, x, y, z)
        self.nodes[label] = n
        if node_set is not None:
            if node_set in self.node_sets:
                self.node_sets[node_set].append(n)
            else:
                self.node_sets[node_set] = [n]
        return n

    # def coordinates(self):
    #    return self.x, self.y, self.z

    def create_element(self, nodes, element_type='C3D8R', element_set=None, label=None):
        node_list = []
        for n in nodes:
            if isinstance(n, Node):
                node_list.append(n)
            if isinstance(n, np.ndarray):
                n = n.flatten().tolist()
            node_list += n
        if label is None:
            e = Element(self.element_counter, node_list, element_type)
        else:
            e = Element(label, node_list, element_type)
        if element_type in self.elements:
            self.elements[element_type].append(e)
        else:
            self.elements[element_type] = [e]
        self.element_counter += 1

        if element_set is not None:
            if element_set in self.element_sets:
                self.element_sets[element_set].append(e)
            else:
                self.element_sets[element_set] = [e]
        return e

    def copy_node_plane(self, nodes, axis, distance, node_set):
        nx, ny = nodes.shape
        axis_idx = xyz_idx[axis]
        new_nodes = np.empty(shape=(nx, ny), dtype=object)
        for i in range(nx):
            for j in range(ny):
                args = [nodes[i, j].x + distance, nodes[i, j].y, nodes[i, j].z]
                args[axis_idx] += distance
                new_nodes[i, j] = self.create_node(*args, node_set=node_set)
        return new_nodes

    @staticmethod
    def _attach_node_plane(nodes_plate, x0=0, y0=0, z0=0,
                           x_neg=None, y_neg=None, z_neg=None, x_pos=None, y_pos=None, z_pos=None):
        if x_pos is not None:
            nodes_plate[-1, :, :] = x_pos
            x0 = x_pos[0, 0]
        if x_neg is not None:
            nodes_plate[0, :, :] = x_neg
            x0 = x_neg[0, 0]

        if y_pos is not None:
            nodes_plate[:, -1, :] = y_pos
            y0 = y_pos[0, 0]
        if y_neg is not None:
            nodes_plate[:, 0, :] = y_neg
            y0 = y_neg[0, 0]

        if z_pos is not None:
            nodes_plate[:, :, -1] = z_pos
            z0 = z_pos[0, 0]
        if z_neg is not None:
            nodes_plate[:, :, 0] = z_neg
            z0 = z_pos[0, 0]

        return nodes_plate, x0, y0, z0

    def create_block(self, nx, ny, nz, dx, dy, dz, x0=0, y0=0, z0=0,
                     x_neg=None, y_neg=None, z_neg=None, x_pos=None, y_pos=None, z_pos=None,
                     node_set='', element_set=''):
        nodes_plate = np.empty(shape=(nx, ny, nz), dtype=object)
        elements_plate = []

        nodes_plate, x0, y0, z0 = self._attach_node_plane(nodes_plate, x0, y0, z0, x_neg, y_neg, z_neg,
                                                          x_pos, y_pos, z_pos)

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if nodes_plate[i, j, k] is None:
                        nodes_plate[i, j, k] = self.create_node(i*dx + x0, j*dy + y0, k*dz + z0, node_set=node_set)
                    if i > 0 and j > 0 and k > 0:
                        e_nodes = [nodes_plate[i - 1, j - 1, k - 1], nodes_plate[i, j - 1, k - 1],
                                   nodes_plate[i - 1, j - 1, k], nodes_plate[i, j - 1, k],
                                   nodes_plate[i - 1, j, k - 1], nodes_plate[i, j, k - 1],
                                   nodes_plate[i - 1, j, k], nodes_plate[i, j, k]]
                        elements_plate.append(self.create_element(e_nodes, element_set=element_set))
        return nodes_plate, elements_plate

    def create_block_axi(self, nx, ny, nz, dx, dy, dz, x0=0, y0=0, z0=0,
                         x_neg=None, y_neg=None, z_neg=None, x_pos=None, y_pos=None, z_pos=None,
                         node_set='', element_set=''):

        nodes_plate = np.empty(shape=(nx, ny, nz), dtype=object)
        elements_plate = []

        nodes_plate, x0, y0, z0 = self._attach_node_plane(nodes_plate, x0, y0, z0, x_neg, y_neg, z_neg,
                                                          x_pos, y_pos, z_pos)

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if nodes_plate[i, j, k] is None:
                        nodes_plate[i, j, k] = self.create_node(i*dx + x0, j*dy + y0, k*dz + z0, node_set=node_set)
                    if i > 0 and j > 0 and k > 0:
                        e_nodes = [nodes_plate[i - 1, j - 1, k - 1], nodes_plate[i, j - 1, k - 1],
                                   nodes_plate[i - 1, j, k - 1], nodes_plate[i, j, k - 1]]
                        elements_plate.append(self.create_element(e_nodes, element_set=element_set,
                                                                  element_type='CAX4'))
        return nodes_plate, elements_plate

    @staticmethod
    def _assign_axes_for_rotation(nodes, rotation_axis, radial_axis):
        if rotation_axis not in 'xyz' and radial_axis not in 'xyz':
            raise ValueError('Rotation axis or radial axis not specified correctly')

        axis1 = radial_axis
        axis2 = 'xyz'.replace(rotation_axis, '').replace(radial_axis, '')

        r_max = 0
        l_max = 0
        for n in nodes:
            r_max = max(r_max, getattr(n, axis1), getattr(n, axis2))
            l_max = max(l_max, getattr(n, radial_axis))

        return axis1, axis2, r_max, l_max

    def transform_square_to_cylinder(self, node_set, rotation_axis, radial_axis, angle, f=0.75):
        nodes = self.node_sets[node_set]

        axis1, axis2, r_max, _ = self._assign_axes_for_rotation(nodes, rotation_axis, radial_axis)

        for n in nodes:
            n1 = getattr(n, axis1)
            n2 = getattr(n, axis2)
            if n1 > n2:
                n2, n1 = n1, n2
            r = n1
            q = n2/n1*angle/2
            dx = r*cos(q) - n1
            dy = r*sin(q) - n2
            k = r/r_max
            setattr(n, axis1, getattr(n, axis1) + dx*k**f)
            setattr(n, axis2, getattr(n, axis2) + dy*k**f)

    def transform_square_to_sector(self, node_set, rotation_axis, radial_axis, angle):
        nodes = self.node_sets[node_set]
        axis1, axis2, r_max, _ = self._assign_axes_for_rotation(nodes, rotation_axis, radial_axis)

        for n in nodes:
            n1 = getattr(n, axis1)
            n2 = getattr(n, axis2)
            if n1 > n2:
                n2, n1 = n1, n2
            r = n1
            if n1 > 0:
                q = n2/n1*angle/2
            else:
                q = 0
            dx = r*cos(q) - n1
            dy = r*sin(q) - n2

            setattr(n, axis1, getattr(n, axis1) + dx)
            setattr(n, axis2, getattr(n, axis2) + dy)

    def sweep_block(self, node_set, rotation_axis, radial_axis, angle):
        nodes = self.node_sets[node_set]
        axis1, axis2, r_max, l_max = self._assign_axes_for_rotation(nodes, rotation_axis, radial_axis)

        for n in nodes:
            n1 = getattr(n, axis1)
            n2 = getattr(n, axis2)
            r = abs(n1)
            if abs(n2) > 0:
                q = n2/l_max*angle
            else:
                q = pi/2
            d1 = r*cos(q) - n1
            d2 = r*sin(q) - n2

            setattr(n, axis1, getattr(n, axis1) + d1)
            setattr(n, axis2, getattr(n, axis2) + d2)

    def create_transition_cell(self, transition_block, axis, element_set='', node_set=''):
        # The mid element
        if axis == 'x':
            d = (transition_block[-1, 0, 0].x - transition_block[0, 0, 0].x)/3
            base_plate = transition_block[0, :, :]
            top_nodes = transition_block[3, 0:4:3, 0:4:3]
        elif axis == 'y':
            d = (transition_block[0, -1, 0].y - transition_block[0, 0, 0].y)/3
            base_plate = transition_block[:, 0, :]
            top_nodes = transition_block[0:4:3, 3, 0:4:3]
        elif axis == 'z':
            d = (transition_block[0, 0, -1].z - transition_block[0, 0, 0].z)/3
            base_plate = transition_block[:, :, 0]
            top_nodes = transition_block[0:4:3, 0:4:3, 3]
        else:
            raise ValueError('Rotation axis or radial axis not specified correctly')

        second_plate = self.copy_node_plane(base_plate, axis, d, node_set)
        center_plate = self.copy_node_plane(base_plate[1:3, 1:3], axis, 3*d/2, node_set)
        mid_plate_x = self.copy_node_plane(base_plate[1:3, 0:4:3], axis, 2*d, node_set)
        mid_plate_y = self.copy_node_plane(base_plate[0:4:3, 1:3], axis, 2*d, node_set)

        # Create the base plate
        nx, ny = base_plate.shape
        for i in range(1, nx):
            for j in range(1, ny):
                e_nodes = [base_plate[i - 1:i + 1, j - 1:j + 1], second_plate[i - 1:i + 1, j - 1:j + 1]]
                self.create_element(e_nodes, element_set=element_set)

        # Create the center element
        e_nodes = [second_plate[1:3, 1:3] + center_plate]
        self.create_element(e_nodes, element_set=element_set)

        # Create the side elements in the "+"
        for i in range(2):
            e_nodes1 = [mid_plate_x[:, i], center_plate[:, i], second_plate[1:3, 2*i:2*i + 2]]
            e_nodes2 = [mid_plate_y[i, :], center_plate[i, :], second_plate[2*i:2*i + 2, 1:3]]

            self.create_element(e_nodes1, element_set=element_set)
            self.create_element(e_nodes2, element_set=element_set)

        # Create the corner elements
        for i in range(2):
            for j in range(2):
                e_nodes = [top_nodes[i, j], second_plate[2*i:2*i + 2, 2*j:2*j + 2], center_plate[i, j],
                           mid_plate_x[i, j], mid_plate_y[i, j]]
                self.create_element(e_nodes, element_set=element_set)

        # Create the "small" center element
        e_nodes = [mid_plate_x, center_plate]
        self.create_element(e_nodes, element_set=element_set)

        # Create the side skewed elements
        for i in range(2):
            e_nodes = [mid_plate_y[i, :], top_nodes[i, :], center_plate[i, :], mid_plate_x[i, :]]
            self.create_element(e_nodes, element_set=element_set)

        # create the top element
        e_nodes = [top_nodes, mid_plate_x]
        self.create_element(e_nodes, element_set=element_set)

    def _assign_bases_and_axes(self, axis, transition_block, node_set):
        if axis == 'x':
            d1 = (transition_block[0, -1, 0].y - transition_block[0, 0, 0].y)/3
            d2 = (transition_block[0, 0, -1].z - transition_block[0, 0, 0].z)/3
            axis1, axis2 = 'y', 'z'
            base1 = transition_block[:, :, 0]
            base2 = transition_block[:, 0, :]
            center_line = self.copy_node_plane(transition_block[:, 1:2, 0], 'z', d1, node_set)
        elif axis == 'y':
            d1 = (transition_block[-1, 0, 0].x - transition_block[0, 0, 0].x)/3
            d2 = (transition_block[0, 0, -1].z - transition_block[0, 0, 0].z)/3
            axis1, axis2 = 'x', 'z'
            base1 = transition_block[0, :, :]
            base2 = transition_block[:, :, 0].transpose()
            center_line = self.copy_node_plane(transition_block[0, :, 1:2], 'x', d1, node_set)

        elif axis == 'z':
            axis1, axis2 = 'x', 'y'
            d1 = (transition_block[-1, 0, 0].x - transition_block[0, 0, 0].x)/3
            d2 = (transition_block[0, -1, 0].y - transition_block[0, 0, 0].y)/3
            base1 = transition_block[0, :, :].transpose()
            base2 = transition_block[:, 0, :].transpose()
            center_line = self.copy_node_plane(transition_block[1:2, 0, :], 'y', d1, node_set).transpose()
        else:
            raise ValueError('Rotation axis or radial axis not specified correctly')
        return d1, d2, axis1, axis2, base1, base2, center_line

    def create_transition_cell_corner(self, transition_block, axis, element_set='', node_set=''):
        d1, d2, axis1, axis2, base1, base2, center_line = self._assign_bases_and_axes(axis, transition_block, node_set)

        mid1 = self.copy_node_plane(base1[:, 1:], axis1, d1, node_set)
        mid2 = self.copy_node_plane(base2[:, 1:], axis2, d2, node_set)

        top1 = self.copy_node_plane(base1[1:3, 3:], axis1, 2*d1, node_set)
        top2 = self.copy_node_plane(base2[1:3, 3:], axis2, 2*d2, node_set)

        center2 = self.copy_node_plane(base1[0:4, 2:], axis1, 2*d1, node_set)

        corner = self.copy_node_plane(base1[0:4:3, 3:], axis1, 3*d1, node_set)

        # create the base plates
        for i in range(1, 4):
            e_nodes = [base1[i - 1:i + 1, 0:2], base2[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base1[i - 1:i + 1, 1:3], mid1[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base2[i - 1:i + 1, 1:3], mid2[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base1[i - 1:i + 1, 2:4], mid1[i - 1:i + 1, 1:3]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base2[i - 1:i + 1, 2:4], mid2[i - 1:i + 1, 1:3]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [center2[i - 1:i + 1, 0], center_line[i - 1:i + 1, 0], mid1[i - 1:i + 1, 1],
                       mid2[i - 1:i + 1, 1]]
            self.create_element(e_nodes, element_set=element_set)

        e_nodes = [mid1[1:3, 1:3], center2[1:3, 0], top1[:, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [mid2[1:3, 1:3], center2[1:3, 0], top2[:, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # creating the corners
        e_nodes = [corner[0, 0], center2[0:2, 0], mid1[0:2, 1:3], top1[0, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [corner[0, 0], center2[0:2, 0], mid2[0:2, 1:3], top2[0, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [corner[1, 0], center2[2:4, 0], mid1[2:4, 1:3], top1[1, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [corner[1, 0], center2[2:4, 0], mid2[2:4, 1:3], top2[1, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # Creating the large element
        e_nodes = [corner[:, 0], top1[:, 0], top2[:, 0], center2[1:3, 0]]
        self.create_element(e_nodes, element_set=element_set)

    def create_transition_cell_corner_out(self, transition_block, axis, element_set='', node_set=''):
        d1, d2, axis1, axis2, base1, base2, center_line = self._assign_bases_and_axes(axis, transition_block, node_set)

        mid1 = self.copy_node_plane(base1[1:3, 1:2], axis2, d2, node_set)
        mid2 = self.copy_node_plane(base2[1:3, 1:2], axis1, d1, node_set)

        edge1 = self.copy_node_plane(base1[0:4:3, 0:1], axis2, 3*d2, node_set)
        edge2 = self.copy_node_plane(base1[0:4:3, 0:1], axis1, 3*d1, node_set)

        center2 = self.copy_node_plane(mid2, axis2, 2*d2, node_set)
        corner = self.copy_node_plane(edge1, axis1, 3*d1, node_set)
        if axis == 'x':
            transition_block[0:4:3, -1, -1] = corner[:, 0]
        elif axis == 'y':
            transition_block[-1, 0:4:3, -1] = corner[:, 0]
        elif axis == 'z':
            transition_block[-1, -1, 0:4:3] = corner[:, 0]

        # create the base row
        for i in range(1, 4):
            e_nodes = [base1[i - 1:i + 1, 0:2], base2[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

        # create the mid sharp elements
        e_nodes = [base1[1:3, 1], mid1, center_line[1:3, 0], center2[:, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base2[1:3, 1], mid2, center_line[1:3, 0], center2[:, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # creating the edge elements
        e_nodes = [base1[0:2, 1], edge1[0, 0], corner[0, 0], center2[0, 0], mid1[0, 0], center_line[0:2, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base2[0:2, 1], edge2[0, 0], corner[0, 0], center2[0, 0], mid2[0, 0], center_line[0:2, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [base1[2:4, 1], edge1[1, 0], corner[1, 0], center2[1, 0], mid1[1, 0], center_line[2:4, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base2[2:4, 1], edge2[1, 0], corner[1, 0], center2[1, 0], mid2[1, 0], center_line[2:4, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # creating the large plates
        e_nodes = [mid1, center2[:, 0], edge1, corner]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [mid2, center2[:, 0], edge2, corner]
        self.create_element(e_nodes, element_set=element_set)

    def create_transition_plate(self, surf, axis, order=1, direction=1, element_set='', node_set=''):
        n2, n3 = surf.shape
        if (n2 - 1)/(3**order) == 0 or (n3 - 1)/(3**order) == 0:
            return
        i = 0
        if axis == 'x':
            block = np.empty(shape=(4, n2, n3), dtype=object)
            block[0, :, :] = surf
            dx = abs(block[0, 0, 1].z - block[0, 0, 0].z)*direction
            block[1, :, :] = self.copy_node_plane(block[0, :, :], 'x', dx, node_set)
            block[3, ::3, ::3] = self.copy_node_plane(block[0, ::3, ::3], 'x', 3*dx, node_set)
            while i + 3 < n2:
                j = 0
                while j + 3 < n3:
                    self.create_transition_cell(block[0:4, i:i + 4, j:j + 4], axis, element_set, node_set)
                    j += 3
                i += 3
            surf = block[-1, ::3, ::3]

        if axis == 'y':
            block = np.empty(shape=(n2, 4, n3), dtype=object)
            block[:, 0, :] = surf
            dy = abs(block[0, 0, 1].z - block[0, 0, 0].z)*direction
            block[:, 1, :] = self.copy_node_plane(block[:, 0, :], 'y', dy, node_set)
            for i in range(n2):
                for j in range(n3):
                    self.create_transition_cell(block[i:i + 4, 0:4, j:j + 4], axis, element_set, node_set)
            surf = block[::3, -1, ::3]
        if axis == 'z':
            block = np.empty(shape=(n2, n3, 4), dtype=object)
            block[:, :, 0] = surf
            dz = abs(block[1, 0, 0].x - block[0, 0, 0].x)*direction
            block[:, :, 1] = self.copy_node_plane(block[:, :, 0], 'z', dz, node_set)

            block[::3, ::3, 3] = self.copy_node_plane(block[::3, ::3, 0], 'z', 3*dz, node_set)
            while i + 3 < n2:
                j = 0
                while j + 3 < n3:
                    self.create_transition_cell(block[i:i + 4, j:j + 4, 0:4], axis, element_set, node_set)
                    j += 3
                i += 3
            surf = block[::3, ::3, -1]

        return self.create_transition_plate(surf, axis, order=order, direction=direction, element_set=element_set,
                                            node_set=node_set)

    def createTransitionCornerOut(self, nodeLine, axes1, axes2, axis3, order=1, eSet='', nSet=''):
        n1 = nodeLine.shape[0]
        if (n1 - 1)/(3**order) == 0:
            return nodeLine
        if len(axes1) == 2:
            dir1, axis1 = -1, axes1[-1]
        else:
            dir1 = 1
        if len(axes2) == 2:
            dir2, axis2 = -1, axes2[-1]
        else:
            dir2 = 1

        if axis3 == 'x':
            d = abs(nodeLine[1].x - nodeLine[0].x)
            nodeBlock = np.empty(shape=((n1, 4, 4)), dtype=object)
            nodeBlock[:, 0, 0] = nodeLine
            nodeBlock[:, 0:1, 1] = self.copy_node_plane(nodeBlock[:, 0:1, 0], 'y', dir1*d, nSet)
            nodeBlock[:, 1, 0:1] = self.copy_node_plane(nodeBlock[:, 0:1, 0], 'z', dir2*d, nSet)
            for i in range(0, n1 + 3, 3):
                self.create_transition_cell_corner_out(nodeBlock[i:i + 4, :, :], 'x', eSet, nSet)
        if axis3 == 'y':
            d = abs(nodeLine[1].y - nodeLine[0].y)
            nodeBlock = np.empty(shape=((4, n1, 4)), dtype=object)
            nodeBlock[0, :, 0] = nodeLine
            nodeBlock[0:1, :, 1] = self.copy_node_plane(nodeBlock[0:1, :, 0], 'z', dir2*d, nSet)
            nodeBlock[1, :, 0:1] = self.copy_node_plane(nodeBlock[0, :, 0:1], 'x', dir1*d, nSet)

            nodeBlock[0:1, ::3, -1] = self.copy_node_plane(nodeBlock[0:1, ::3, 0], 'z', 3*dir2*d, nSet)
            nodeBlock[-1, ::3, 0:1] = self.copy_node_plane(nodeBlock[0, ::3, 0:1], 'x', 3*dir1*d, nSet)
            for i in range(0, n1 - 1, 3):
                self.create_transition_cell_corner_out(nodeBlock[:, i:i + 4, :], 'y', eSet, nSet)
            nodeLine = nodeBlock[-1, ::3, -1]
            return self.createTransitionCornerOut(nodeLine, axes1, axes2, axis3, order, eSet, nSet)

        if axis3 == 'z':
            d = abs(nodeLine[1].z - nodeLine[0].z)
            nodeBlock = np.empty(shape=((4, 4, n1)), dtype=object)
            nodeBlock[0, 0, :] = nodeLine
            nodeBlock[0:1, 1, :] = self.copy_node_plane(nodeBlock[0:1, 0, :], 'x', dir1*d, nSet)
            nodeBlock[1, 0:1, :] = self.copy_node_plane(nodeBlock[0:1, 0, :], 'y', dir2*d, nSet)
            for i in range(0, n1, 3):
                self.create_transition_cell_corner_out(nodeBlock[:, :, i:i + 4], 'z', eSet, nSet)

    def createTransitionCornerOut2D(self, node_line_1, node_line_2, eSet='', nSet=''):

        nodeBlock = np.empty(shape=((4, 4, 1)), dtype=object)
        nodeBlock[0, 0, 0] = node_line_1[0]
        nodeBlock[1, 0, 0] = node_line_1[1]
        nodeBlock[3, 0, 0] = node_line_1[2]

        nodeBlock[0, 1, 0] = node_line_2[1]
        nodeBlock[0, 3, 0] = node_line_2[2]

        nodeBlock[1, 1, 0] = self.create_node(nodeBlock[1, 0, 0].x, nodeBlock[0, 1, 0].y, 0, nSet)
        nodeBlock[3, 3, 0] = self.create_node(nodeBlock[3, 0, 0].x, nodeBlock[0, 3, 0].y, 0, nSet)

        self.create_element([nodeBlock[0, 0, 0], nodeBlock[0, 1, 0], nodeBlock[1, 0, 0], nodeBlock[1, 1, 0]],
                            element_set=eSet, element_type='CAX4')
        self.create_element([nodeBlock[1, 0, 0], nodeBlock[1, 1, 0], nodeBlock[3, 0, 0], nodeBlock[3, 3, 0]],
                            element_set=eSet, element_type='CAX4')
        self.create_element([nodeBlock[0, 1, 0], nodeBlock[0, 3, 0], nodeBlock[3, 3, 0], nodeBlock[1, 1, 0]],
                            element_set=eSet, element_type='CAX4')

    def createTransitionCorner(self, surf1, surf2, eSet='', nSet='', order=1):
        nx = surf1.shape[0]
        ny = surf1.shape[1]
        nz = surf2.shape[1]
        nodesPlate = np.empty(shape=((nx, ny, nz)), dtype=object)
        nodesPlate[:, :, 0] = surf1
        nodesPlate[0, :, :] = surf2

        if (nx - 1)/3**order == 0 or (ny - 1)/3**order == 0 or (nz - 1)/3**order == 0:
            for i in range(1, nx):
                dx = nodesPlate[i, 0, 0].x - nodesPlate[0, 0, 0].x

                nodesPlate[i, :, :] = self.copy_node_plane(nodesPlate[0, :, :], 'x', dx, nSet)
                for j in range(1, ny):
                    for k in range(1, nz):
                        eNodes = nodesPlate[i - 1:i + 1, j - 1:j + 1, k - 1:k + 1].flatten().tolist()
                        self.create_element(eNodes, element_set=eSet)
            return

            # Create the first layer in z-direction
        k = 0
        i = 3

        distance = nodesPlate[3, 0, 0].x - nodesPlate[0, 0, 0].x
        i = 0
        while i + 1 < ny:
            transitionBlock = nodesPlate[0:4, i:i + 4, 0:4]
            self.create_transition_cell_corner(transitionBlock, 'y', element_set=eSet)
            i += 3

        i = 3
        while i + 3 < nx:
            j = 0
            while j + 3 < ny:
                # creating the 4 upper nodes
                cornerNodes = nodesPlate[i:i + 4:3, j:j + 4:3, k]
                nodesPlate[i:(i + 4):3, j:(j + 4):3, k + 3] = self.copy_node_plane(cornerNodes,
                                                                                 'z',
                                                                                   -distance, nSet)
                transitionBlock = nodesPlate[i:i + 4, j:j + 4, k:k + 4]
                self.create_transition_cell(transitionBlock, 'z', element_set=eSet, node_set=nSet)
                j += 3
            i += 3

        # Create the first layer in y-direction
        i = 3
        k = 0
        while i + 3 < nz:
            j = 0
            while j + 3 < ny:
                # creating the 4 upper nodes
                cornerNodes = nodesPlate[k, j:j + 4:3, i:i + 4:3]
                nodesPlate[k + 3, j:(j + 4):3, i:(i + 4):3] = self.copy_node_plane(cornerNodes,
                                                                                 'x',
                                                                                   distance, nSet)
                transitionBlock = nodesPlate[k:k + 4, j:j + 4, i:i + 4]
                self.create_transition_cell(transitionBlock, 'x', element_set=eSet, node_set=nSet)
                j += 3
            i += 3

        surf1 = nodesPlate[3::3, ::3, 3]
        surf2 = nodesPlate[3, ::3, 3::3]
        return self.createTransitionCorner(surf1, surf2, eSet=eSet, nSet=nSet, order=order)

    def create2DTransition(self, axis1, axis2, axis3, x0, y0, z0, d1, d2, d3, eSet='', nSet=''):
        # assume that axis1 is x, 2 is y, z is 3
        nodes = np.empty(shape=((2, 4, 4)), dtype=object)

        # creating the base plate
        for i in range(2):
            for j in range(4):
                nodes[i, j, 0] = self.create_node(d1*i, d2*j, 0, nSet)
                nodes[i, j, 1] = self.create_node(d1*i, d2*j, d3, nSet)
            nodes[i, 1, 2] = self.create_node(d1*i, d2, 2*d3, nSet)
            nodes[i, 2, 2] = self.create_node(d1*i, 2*d2, 2*d3, nSet)
            nodes[i, 0, 3] = self.create_node(d1*i, 0, 3*d3, nSet)
            nodes[i, 3, 3] = self.create_node(d1*i, 3*d2, 3*d3, nSet)

        for i in range(2):
            for j in range(4):
                for k in range(4):
                    if nodes[i, j, k] is not None:
                        n = nodes[i, j, k]
                        x, y, z = n.x, n.y, n.z
                        if axis1 is not 'x':
                            if axis1 is 'y':
                                n.x = y
                            if axis1 is 'z':
                                n.x = z
                        if axis2 is not 'y':
                            if axis2 is 'x':
                                n.y = x
                            if axis2 is 'z':
                                n.y = z
                        if axis3 is not 'z':
                            if axis3 is 'x':
                                n.z = x
                            if axis3 is 'y':
                                n.z = y
        for n in nodes.flatten().flatten().flatten():
            if n is not None:
                n.x += x0
                n.y += y0
                n.z += z0

        # create the base layer
        for i in range(1, 4):
            eNodes = nodes[:, i - 1:i + 1, 0:2].flatten().flatten().tolist()
            self.create_element(eNodes, element_set=eSet)
        # the center element
        eNodes = nodes[:, 1:3, 1:3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet)
        # create the corner elements
        eNodes = nodes[:, 0, 1:4:2].flatten().tolist() + nodes[:, 1, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet)
        eNodes = nodes[:, 3, 1:4:2].flatten().tolist() + nodes[:, 2, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet)
        # create the top element
        eNodes = nodes[:, 1:3, 2].flatten().flatten().tolist() + nodes[:, 0:4:3, 3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

    def create2DTransitionAxi(self, axis1, axis2, axis3, x0, y0, z0, d1, d2, d3, eSet='', nSet=''):
        # assume that axis1 is x, 2 is y, z is 3
        nodes = np.empty(shape=((1, 4, 4)), dtype=object)

        # creating the base plate
        for i in range(1):
            for j in range(4):
                nodes[i, j, 0] = self.create_node(d1*i, d2*j, 0, nSet)
                nodes[i, j, 1] = self.create_node(d1*i, d2*j, d3, nSet)
            nodes[i, 1, 2] = self.create_node(d1*i, d2, 2*d3, nSet)
            nodes[i, 2, 2] = self.create_node(d1*i, 2*d2, 2*d3, nSet)
            nodes[i, 0, 3] = self.create_node(d1*i, 0, 3*d3, nSet)
            nodes[i, 3, 3] = self.create_node(d1*i, 3*d2, 3*d3, nSet)

        for i in range(1):
            for j in range(4):
                for k in range(4):
                    if nodes[i, j, k] is not None:
                        n = nodes[i, j, k]
                        x, y, z = n.x, n.y, n.z
                        if axis1 is not 'x':
                            if axis1 is 'y':
                                n.x = y
                            if axis1 is 'z':
                                n.x = z
                        if axis2 is not 'y':
                            if axis2 is 'x':
                                n.y = x
                            if axis2 is 'z':
                                n.y = z
                        if axis3 is not 'z':
                            if axis3 is 'x':
                                n.z = x
                            if axis3 is 'y':
                                n.z = y
        for n in nodes.flatten().flatten().flatten():
            if n is not None:
                n.x += x0
                n.y += y0
                n.z += z0

        # create the base layer
        for i in range(1, 4):
            eNodes = nodes[:, i - 1:i + 1, 0:2].flatten().flatten().tolist()
            self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        # the center element
        eNodes = nodes[:, 1:3, 1:3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        # create the corner elements
        eNodes = nodes[:, 0, 1:4:2].flatten().tolist() + nodes[:, 1, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        eNodes = nodes[:, 3, 1:4:2].flatten().tolist() + nodes[:, 2, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        # create the top element
        eNodes = nodes[:, 1:3, 2].flatten().flatten().tolist() + nodes[:, 0:4:3, 3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')

    def noOfElements(self):
        return len(self.elements)

    def noOfNodes(self):
        return len(self.nodes)

    def listsForPart(self):
        nIDs = []
        coords = []
        for label, n in self.nodes.iteritems():
            nIDs.append(label)
            coords.append([n.x, n.y, n.z])
        eData = []
        for eType in self.elements.keys():
            eIDs = []
            conn = []
            for e in self.elements[eType]:
                eIDs.append(e.ID)
                conn.append([n.ID for n in e.nodes])
            eData.append([eType, eIDs, conn])
        return [nIDs, coords], eData

    def copyElementSet(self, oldSet, newSet, nSet='', axisOrder='xyz'):
        elements = self.element_sets[oldSet]
        for e in elements:
            eNodes = []
            for n in e.nodes:
                if axisOrder == 'xyz':
                    x, y, z = n.x, n.y, n.z
                if axisOrder == 'yzx':
                    x, y, z = n.y, n.z, n.x
                if axisOrder == 'zxy':
                    x, y, z = n.z, n.x, n.y

                if axisOrder == 'yxz':
                    x, y, z = n.y, n.x, n.z
                if axisOrder == 'xzy':
                    x, y, z = n.x, n.z, n.y
                if axisOrder == 'zyx':
                    x, y, z = n.z, n.y, n.x
                eNodes.append(self.create_node(x, y, z, nSet))
            self.create_element(eNodes, element_type=e.eType, element_set=newSet)

    def addToNodeSet(self, nodes, nodeSet):
        if type(nodes).__module__ is 'numpy':
            while len(nodes.shape) > 1:
                nodes = nodes.flatten()
        if not nodeSet in self.node_sets:
            self.node_sets[nodeSet] = []
        for n in nodes:
            self.node_sets[nodeSet].append(n)

    def getBoundingBox(self, nSet=''):
        xMin = 1E99
        xMax = -1E99
        yMin = 1E99
        yMax = -1E99
        zMin = 1E99
        zMax = -1E99
        for _, n in self.nodes.iteritems():
            xMin = min(xMin, n.x)
            yMin = min(yMin, n.y)
            zMin = min(zMin, n.z)

            xMax = max(xMax, n.x)
            yMax = max(yMax, n.y)
            zMax = max(zMax, n.z)
        return xMin, xMax, yMin, yMax, zMin, zMax

    def getNodesByBoundingBox(self, xMin=-1E88, xMax=1E88, yMin=-1E88, yMax=1E88,
                              zMin=-1E88, zMax=1E88, nSet=''):
        nodes = []
        if nSet == '':
            nodeList = self.nodes.iteritems()
            for _, n in nodeList:
                if n.x >= xMin and n.x <= xMax:
                    if n.y >= yMin and n.y <= yMax:
                        if n.z >= zMin and n.z <= zMax:
                            nodes.append(n)

        else:
            nodeList = self.node_sets[nSet]
            for n in nodeList:
                if n.x >= xMin and n.x <= xMax:
                    if n.y >= yMin and n.y <= yMax:
                        if n.z >= zMin and n.z <= zMax:
                            nodes.append(n)

        return nodes
