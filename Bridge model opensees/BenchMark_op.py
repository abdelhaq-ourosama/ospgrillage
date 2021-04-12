# Grillage generator wizard
# Model name: BenchMark
# Constructed on:12/04/2021 13:13:30
import numpy as np
import math
import openseespy.opensees as ops
import openseespy.postprocessing.Get_Rendering as opsplt
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)
# create transformation 1
ops.geomTransf("Linear", 1, *[0, 0, 1])
# create transformation 2
ops.geomTransf("Linear", 2, *[0.9063077870366499, 0, 0.42261826174069944])
# Node generation procedure
ops.node(1, 0.0, 0, 0.0)
ops.node(2, 0.8333333333333334, 0, 0.0)
ops.node(3, 1.6666666666666667, 0, 0.0)
ops.node(4, 2.5, 0, 0.0)
ops.node(5, 3.3333333333333335, 0, 0.0)
ops.node(6, 4.166666666666667, 0, 0.0)
ops.node(7, 5.0, 0, 0.0)
ops.node(8, 5.833333333333334, 0, 0.0)
ops.node(9, 6.666666666666667, 0, 0.0)
ops.node(10, 7.5, 0, 0.0)
ops.node(11, 8.333333333333334, 0, 0.0)
ops.node(12, 9.166666666666668, 0, 0.0)
ops.node(13, 10.0, 0, 0.0)
ops.node(14, -0.4663076581549986, 0, 1.0)
ops.node(15, 0.3670256751783348, 0, 1.0)
ops.node(16, 1.2003590085116682, 0, 1.0)
ops.node(17, 2.0336923418450015, 0, 1.0)
ops.node(18, 2.867025675178335, 0, 1.0)
ops.node(19, 3.7003590085116684, 0, 1.0)
ops.node(20, 4.5336923418450015, 0, 1.0)
ops.node(21, 5.367025675178335, 0, 1.0)
ops.node(22, 6.200359008511668, 0, 1.0)
ops.node(23, 7.0336923418450015, 0, 1.0)
ops.node(24, 7.867025675178335, 0, 1.0)
ops.node(25, 8.700359008511668, 0, 1.0)
ops.node(26, 9.533692341845, 0, 1.0)
ops.node(27, -0.9326153163099972, 0, 2.0)
ops.node(28, -0.0992819829766638, 0, 2.0)
ops.node(29, 0.7340513503566696, 0, 2.0)
ops.node(30, 1.567384683690003, 0, 2.0)
ops.node(31, 2.4007180170233364, 0, 2.0)
ops.node(32, 3.23405135035667, 0, 2.0)
ops.node(33, 4.067384683690003, 0, 2.0)
ops.node(34, 4.900718017023337, 0, 2.0)
ops.node(35, 5.73405135035667, 0, 2.0)
ops.node(36, 6.567384683690003, 0, 2.0)
ops.node(37, 7.400718017023337, 0, 2.0)
ops.node(38, 8.23405135035667, 0, 2.0)
ops.node(39, 9.067384683690003, 0, 2.0)
ops.node(40, -1.3989229744649958, 0, 3.0)
ops.node(41, -0.5655896411316624, 0, 3.0)
ops.node(42, 0.26774369220167094, 0, 3.0)
ops.node(43, 1.1010770255350042, 0, 3.0)
ops.node(44, 1.9344103588683377, 0, 3.0)
ops.node(45, 2.7677436922016714, 0, 3.0)
ops.node(46, 3.6010770255350044, 0, 3.0)
ops.node(47, 4.434410358868338, 0, 3.0)
ops.node(48, 5.267743692201671, 0, 3.0)
ops.node(49, 6.101077025535004, 0, 3.0)
ops.node(50, 6.934410358868338, 0, 3.0)
ops.node(51, 7.767743692201672, 0, 3.0)
ops.node(52, 8.601077025535004, 0, 3.0)
ops.node(53, -1.8652306326199943, 0, 4.0)
ops.node(54, -1.031897299286661, 0, 4.0)
ops.node(55, -0.1985639659533276, 0, 4.0)
ops.node(56, 0.6347693673800057, 0, 4.0)
ops.node(57, 1.4681027007133391, 0, 4.0)
ops.node(58, 2.301436034046673, 0, 4.0)
ops.node(59, 3.134769367380006, 0, 4.0)
ops.node(60, 3.96810270071334, 0, 4.0)
ops.node(61, 4.801436034046673, 0, 4.0)
ops.node(62, 5.634769367380006, 0, 4.0)
ops.node(63, 6.46810270071334, 0, 4.0)
ops.node(64, 7.301436034046674, 0, 4.0)
ops.node(65, 8.134769367380006, 0, 4.0)
ops.node(66, -2.331538290774993, 0, 5.0)
ops.node(67, -1.4982049574416596, 0, 5.0)
ops.node(68, -0.6648716241083263, 0, 5.0)
ops.node(69, 0.16846170922500692, 0, 5.0)
ops.node(70, 1.0017950425583404, 0, 5.0)
ops.node(71, 1.8351283758916739, 0, 5.0)
ops.node(72, 2.668461709225007, 0, 5.0)
ops.node(73, 3.501795042558341, 0, 5.0)
ops.node(74, 4.335128375891674, 0, 5.0)
ops.node(75, 5.1684617092250065, 0, 5.0)
ops.node(76, 6.00179504255834, 0, 5.0)
ops.node(77, 6.835128375891674, 0, 5.0)
ops.node(78, 7.6684617092250065, 0, 5.0)
# Boundary condition implementation
ops.fix(1, *[1, 1, 1, 0, 0, 0])
ops.fix(14, *[1, 1, 1, 0, 0, 0])
ops.fix(27, *[1, 1, 1, 0, 0, 0])
ops.fix(40, *[1, 1, 1, 0, 0, 0])
ops.fix(53, *[1, 1, 1, 0, 0, 0])
ops.fix(66, *[1, 1, 1, 0, 0, 0])
ops.fix(13, *[0, 1, 1, 0, 0, 0])
ops.fix(26, *[0, 1, 1, 0, 0, 0])
ops.fix(39, *[0, 1, 1, 0, 0, 0])
ops.fix(52, *[0, 1, 1, 0, 0, 0])
ops.fix(65, *[0, 1, 1, 0, 0, 0])
ops.fix(78, *[0, 1, 1, 0, 0, 0])
# Material definition 
ops.uniaxialMaterial("Concrete01", 1, *[-6.0, -0.004, -6.0, -0.014])
# Element generation for section: long_mem
ops.element("elasticBeamColumn", 26, *[14,15], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 28, *[15,16], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 30, *[16,17], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 32, *[17,18], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 34, *[18,19], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 36, *[19,20], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 38, *[20,21], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 40, *[21,22], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 42, *[22,23], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 44, *[23,24], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 46, *[24,25], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 48, *[25,26], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 51, *[27,28], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 53, *[28,29], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 55, *[29,30], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 57, *[30,31], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 59, *[31,32], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 61, *[32,33], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 63, *[33,34], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 65, *[34,35], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 67, *[35,36], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 69, *[36,37], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 71, *[37,38], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 73, *[38,39], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 76, *[40,41], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 78, *[41,42], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 80, *[42,43], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 82, *[43,44], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 84, *[44,45], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 86, *[45,46], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 88, *[46,47], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 90, *[47,48], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 92, *[48,49], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 94, *[49,50], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 96, *[50,51], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 98, *[51,52], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 101, *[53,54], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 103, *[54,55], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 105, *[55,56], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 107, *[56,57], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 109, *[57,58], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 111, *[58,59], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 113, *[59,60], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 115, *[60,61], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 117, *[61,62], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 119, *[62,63], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 121, *[63,64], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
ops.element("elasticBeamColumn", 123, *[64,65], *[34700000000.0, 20000000000.0, 0.896, 0.133, 0.213, 0.259], 1)
# Element generation for section: long_edge_1
ops.element("elasticBeamColumn", 1, *[1,2], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 3, *[2,3], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 5, *[3,4], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 7, *[4,5], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 9, *[5,6], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 11, *[6,7], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 13, *[7,8], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 15, *[8,9], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 17, *[9,10], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 19, *[10,11], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 21, *[11,12], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 23, *[12,13], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 126, *[66,67], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 127, *[67,68], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 128, *[68,69], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 129, *[69,70], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 130, *[70,71], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 131, *[71,72], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 132, *[72,73], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 133, *[73,74], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 134, *[74,75], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 135, *[75,76], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 136, *[76,77], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
ops.element("elasticBeamColumn", 137, *[77,78], *[34700000000.0, 20000000000.0, 0.044625, 0.00026, 0.00011, 0.000242], 1)
# Element generation for section: trans_mem
ops.element("elasticBeamColumn", 4, *[2,15], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 6, *[3,16], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 8, *[4,17], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 10, *[5,18], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 12, *[6,19], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 14, *[7,20], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 16, *[8,21], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 18, *[9,22], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 20, *[10,23], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 22, *[11,24], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 24, *[12,25], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 29, *[15,28], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 31, *[16,29], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 33, *[17,30], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 35, *[18,31], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 37, *[19,32], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 39, *[20,33], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 41, *[21,34], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 43, *[22,35], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 45, *[23,36], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 47, *[24,37], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 49, *[25,38], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 54, *[28,41], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 56, *[29,42], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 58, *[30,43], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 60, *[31,44], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 62, *[32,45], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 64, *[33,46], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 66, *[34,47], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 68, *[35,48], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 70, *[36,49], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 72, *[37,50], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 74, *[38,51], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 79, *[41,54], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 81, *[42,55], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 83, *[43,56], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 85, *[44,57], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 87, *[45,58], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 89, *[46,59], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 91, *[47,60], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 93, *[48,61], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 95, *[49,62], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 97, *[50,63], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 99, *[51,64], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 104, *[54,67], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 106, *[55,68], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 108, *[56,69], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 110, *[57,70], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 112, *[58,71], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 114, *[59,72], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 116, *[60,73], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 118, *[61,74], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 120, *[62,75], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 122, *[63,76], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
ops.element("elasticBeamColumn", 124, *[64,77], *[34700000000.0, 20000000000.0, 0.04428, 0.00228, 0.223, 0.0012], 2)
# Element generation for section: trans_edge_1
ops.element("elasticBeamColumn", 2, *[1,14], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 27, *[14,27], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 52, *[27,40], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 77, *[40,53], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 102, *[53,66], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
# Element generation for section: trans_edge_2
ops.element("elasticBeamColumn", 25, *[13,26], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 50, *[26,39], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 75, *[39,52], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 100, *[52,65], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
ops.element("elasticBeamColumn", 125, *[65,78], *[34700000000.0, 20000000000.0, 0.02214, 0.00217, 0.111, 0.000597], 2)
