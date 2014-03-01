# -*- coding: utf-8 -*-
import json
import os

import alp


class HuePresetsFilter:

    def get_results(self, query):
        results = []
        partial_query = None

        if query.startswith('save:'):
            control = query.split(':')
            preset_name = control[1]

            results.append(alp.Item(
                title=u'Save current state as…',
                arg=json.dumps({
                    'action': 'save_preset',
                    'preset_name': preset_name,
                }),
            ))
        else:
            partial_query = query

            results.append(alp.Item(
                title=u'Save current state as…',
                valid=False,
                autocomplete='presets save:',
            ))
            for _, dirnames, __ in os.walk(alp.storage(join='presets')):
                for subdirname in dirnames:
                    results.append(alp.Item(
                        title=subdirname,
                        icon='icons/preset.png',
                        autocomplete=subdirname,
                        arg=json.dumps({
                            'action': 'load_preset',
                            'preset_name': subdirname
                        }),
                    ))

        if partial_query:
            results = [
                result
                for result in results
                if partial_query.lower() in result.autocomplete.lower()
            ]

        return results


if __name__ == '__main__':
    presets_filter = HuePresetsFilter()
    results = presets_filter.get_results(alp.args()[0])
    alp.feedback(results)
