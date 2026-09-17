from skills_extractor import extract_skills


def test_cpp_detected():
    assert "C++" in extract_skills("Experience with C++ and STL")


def test_ros_detected_standalone():
    assert "ROS" in extract_skills("Built a robot using ROS and Python")


def test_ros_not_falsely_matched_inside_microsoft():
    skills = extract_skills("Interned at Microsoft using Azure")
    assert "ROS" not in skills


def test_node_js_variants_normalized():
    assert "Node.js" in extract_skills("Backend built with Node.js")
    assert "Node.js" in extract_skills("Backend built with NodeJS")
    assert "Node.js" in extract_skills("Backend built with Node JS")


def test_fpga_and_arduino_detected():
    skills = extract_skills("Designed FPGA firmware and used Arduino")
    assert "FPGA" in skills
    assert "Arduino" in skills


def test_no_skills_in_unrelated_text():
    skills = extract_skills("I enjoy hiking and playing guitar")
    assert skills == []
