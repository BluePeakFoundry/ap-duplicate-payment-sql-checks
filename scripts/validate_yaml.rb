#!/usr/bin/env ruby
require 'yaml'
YAML.load_file('action.yml')
YAML.load_file('.github/workflows/ap-duplicate-payment-audit.yml')
puts 'YAML_OK'
