# -*- coding: utf-8 -*-
import yaml

import alp


class HueFilterBase:

    items_yaml = ''

    # A list of alp.Item
    results = []

    # For filtering results at the end to add a simple autocomplete
    partial_query = None

    def __init__(self):
        self.items = yaml.load(self.items_yaml)

    def _add_item(self, string_key=None, **kwargs):
        """A convenient way of adding items based on the yaml data."""
        if string_key and self.items.get(string_key):
            for k, v in self.items[string_key].items():
                kwargs.setdefault(k, v)

        self.results.append(alp.Item(**kwargs))

    def _partial_query_filter(self, result):
        """Returns True if the result is valid match for the partial query, else False.

            Args:
                result - an instance of alp.Item
        """
        if self.partial_query:
            return (self.partial_query.lower() in result.autocomplete.lower())
        else:
            return True

    def _filter_results(self):
        self.results = [r for r in self.results if self._partial_query_filter(r)]
