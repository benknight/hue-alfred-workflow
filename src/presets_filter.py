# -*- coding: utf-8 -*-
import json
import os

import alp

from base_filter import HueFilterBase


class HuePresetsFilter(HueFilterBase):

    ICON = 'icons/preset.png'

    def get_results(self, query):
        self.partial_query = query

        for _, dirnames, __ in os.walk(alp.storage(join='presets')):
            for subdirname in dirnames:
                self._add_item(
                    title=subdirname,
                    icon=self.ICON,
                    autocomplete=subdirname,
                    arg=json.dumps({
                        'action': 'load_preset',
                        'preset_name': subdirname,
                    }),
                )

        if not self.results:
            self._add_item(
                title='You have no saved presets!',
                subtitle='Use "-hue save-preset" to save the current lights state as a preset.',
                icon=self.ICON,
                valid=False,
            )

        self._filter_results()
        return self.results


if __name__ == '__main__':
    presets_filter = HuePresetsFilter()
    results = presets_filter.get_results(alp.args()[0])
    alp.feedback(results)
