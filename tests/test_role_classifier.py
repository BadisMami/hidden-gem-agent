from role_classifier import classify_role


def test_swe_titles():
    assert classify_role("Software Engineering Intern") == "SWE"
    assert classify_role(
        "Software Quality Assurance Engineering Intern"
    ) == "SWE"


def test_ml_title():
    assert classify_role("Machine Learning Intern") == "ML"


def test_data_title():
    assert classify_role("Data Science Intern") == "Data"


def test_embedded_beats_swe():
    assert classify_role("Embedded Software Intern") == "Embedded"


def test_firmware_title():
    assert classify_role("Firmware Engineering Intern") == "Firmware"


def test_fpga_classified_as_hardware():
    assert classify_role("FPGA Intern") == "Hardware"


def test_robotics_beats_swe():
    assert classify_role("Robotics Software Intern") == "Robotics"


def test_product_management_not_swe():
    assert classify_role("Product Management Intern") == "Product"


def test_unclassifiable_title_is_other():
    assert classify_role("Accounting Intern") == "Other"


def test_empty_title_is_other():
    assert classify_role("") == "Other"
    assert classify_role(None) == "Other"


def test_cybersecurity_title():
    assert classify_role("Cybersecurity Analyst Intern") == "Cybersecurity"
