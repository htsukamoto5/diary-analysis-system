from class_sys_builder import *

def test_class_sys_builder_construction(self):
    # Create an instance of class_sys_builder class (calling the constructor)
    csb1 = ClassSysBuilder()
    csb2 = ClassSysBuilder()
    self.assertIsNot(csb1, csb2)
