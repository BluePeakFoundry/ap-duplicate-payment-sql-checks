#!/usr/bin/env ruby
require 'yaml'
YAML.load_file('action.yml')
YAML.load_file('.github/workflows/ap-duplicate-payment-audit.yml')
YAML.load_file('.github/ISSUE_TEMPLATE/ap-sql-review.yml')
YAML.load_file('.github/ISSUE_TEMPLATE/ap-service-scope.yml')
puts 'YAML_OK'
