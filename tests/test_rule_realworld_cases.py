
import unittest
import subprocess
import os
import tempfile
import shutil

class TestRuleValidationRealWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.main_script = os.path.join(cls.base_dir, "main.py")
        cls.sample_data_dir = os.path.join(cls.base_dir, "sample_data")
        cls.rules_dir = tempfile.mkdtemp()

        os.makedirs(cls.sample_data_dir, exist_ok=True)

        # TC1: email has 33% missing (2 of 6)
        cls.tc1_csv = os.path.join(cls.sample_data_dir, "tc1_email_missing.csv")
        with open(cls.tc1_csv, "w") as f:
            f.write("email,age\n")
            f.write("a@a.com,23\n")
            f.write("b@b.com,45\n")
            f.write(",50\n")
            f.write("c@c.com,29\n")
            f.write("d@d.com,32\n")
            f.write(",41\n")

        cls.tc1_rules = os.path.join(cls.rules_dir, "tc1_rules.yaml")
        with open(cls.tc1_rules, "w") as f:
            f.write("rules:\n")
            f.write("  - rule: missing_rate(email) < 0.1\n")
            f.write("    severity: error\n")

        # TC2: mean(age) = 45.3, should pass
        cls.tc2_csv = os.path.join(cls.sample_data_dir, "tc2_mean_age.csv")
        with open(cls.tc2_csv, "w") as f:
            f.write("email,age\n")
            f.write("a@a.com,45\n")
            f.write("b@b.com,46\n")
            f.write("c@c.com,45\n")

        cls.tc2_rules = os.path.join(cls.rules_dir, "tc2_rules.yaml")
        with open(cls.tc2_rules, "w") as f:
            f.write("rules:\n")
            f.write("  - rule: mean(age) < 50\n")
            f.write("    severity: warn\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.rules_dir)
        os.remove(cls.tc1_csv)
        os.remove(cls.tc2_csv)

    def test_tc1_missing_rate(self):
        result = subprocess.run(
            ["python", self.main_script, self.tc1_csv, "--rules", self.tc1_rules],
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        print("[DEBUG TC1] ReturnCode:", result.returncode)
        print("[DEBUG TC1] Output:", output)
        if "Rule validation is disabled" in output:
            self.assertIn("Skipping rule validation", output)
        else:
            self.assertEqual(result.returncode, 2)

    def test_tc2_mean_pass(self):
        result = subprocess.run(
            ["python", self.main_script, self.tc2_csv, "--rules", self.tc2_rules],
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        print("[DEBUG TC2] ReturnCode:", result.returncode)
        print("[DEBUG TC2] Output:", output)
        self.assertEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()
