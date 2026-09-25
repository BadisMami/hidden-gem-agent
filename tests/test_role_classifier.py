import pytest

from role_classifier import classify_role, is_grad_only


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


@pytest.mark.parametrize("title", [
    "Current PhD, AI Engineering Internship Program - Summer 2027",
    "2027 Summer Internship - PhD Data Science",
    "Ph.D. Robotics Intern",
    "Current Master's - Data Science Internship",
    "Masters Software Engineering Intern",
    "MBA Intern, Finance Leadership Development Program",
    "Doctoral Research Intern",
    "Graduate Student Embedded Intern",
])
def test_grad_only_titles_detected(title):
    assert is_grad_only(title) is True


@pytest.mark.parametrize("title", [
    "Software Engineering Intern",
    "Software Engineer - Undergrad Internship - Summer 2027",
    "Internship - 2027 Undergraduate and Master's Research & Development Intern",
    "Embedded Systems Intern",
    "Microsoft Office / MS Excel Intern",
    "Intern and New Grad Opportunities",
    "Mastercard Software Engineering Intern",
])
def test_undergrad_titles_not_flagged(title):
    assert is_grad_only(title) is False
