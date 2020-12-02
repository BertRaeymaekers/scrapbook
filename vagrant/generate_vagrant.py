#!/usr/bin/env python3


import json
import os
import pathlib
import sys

import jinja2


def generate_vagrant(config, template_path, template_name=None):
    if not template_name:
        template_name = 'Vagrantfile.j2'
    template_path = pathlib.Path(template_path)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_path)))
    template = env.get_template(template_name)
    for item, params in config.items():
        try:
            os.mkdir(template_path / item)
        except FileExistsError:
            pass
        filename = template_path / item / template_name.rsplit('.', 1)[0]
        with open(filename, 'w') as output_file:
            rendered_output = template.render(**params)
            output_file.write(rendered_output)
            yield (item, filename)


if __name__ == '__main__':
    try:
        work_path = pathlib.Path(sys.argv[1])
    except IndexError:
        # No parameter passed, use the current working directory
        work_path = pathlib.Path.cwd()
    print("Reading in config...")
    with open(work_path / 'config.json') as json_file:
        config = json.load(json_file)
    print("Generating for %s..." % (work_path))
    for tag, generated in generate_vagrant(config, work_path):
        print("\t%s: %s" % (tag, generated))

