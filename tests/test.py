import os
import json
import pandas


class TestMixin:
    def load_fixture(self, fixture):
        fixture = os.path.join(os.path.dirname(__file__), fixture)
        with open(fixture, 'r') as f:
            return json.load(f)

    def load_csv(self, fixture):
        fixture = os.path.join(os.path.dirname(__file__), fixture)
        return pandas.read_csv(fixture)
