#!/usr/bin/python

# This script is used to convert .yaml files to patterns and package groups.
# Copyright (C) 2011 Marko Saukko <FIRSTNAME.LASTNAME@gmail.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# This script is based on MeeGo package-group scripts
# https://meego.gitorious.org/meego-os-base/package-groups/

import yaml
import sys, os
import optparse
from lxml import etree

rpm_ns="http://linux.duke.edu/metadata/rpm"
pattern_ns="http://novell.com/package/metadata/suse/pattern"
NSMAP = {None : pattern_ns, "rpm": rpm_ns}

NSMAP_GROUP = {None : pattern_ns, "rpm": rpm_ns, "patterns": pattern_ns}

TMP_FILE = "xmllint_tmp.xml"

def process_yaml(stream, proot, newobsapi):
	y = yaml.load(stream)

	# <name>
	etree.SubElement(proot, "name").text = y['Name']
	
	# Old OBS isn't able to handle these options.
	if newobsapi:
		# <version>
		if y.has_key('Version'):
			etree.SubElement(proot, "version").attrib['ver'] = "%s" % y['Version']
		
		# <arch>
		if y.has_key('Arch'):
			etree.SubElement(proot, "arch").text = "%s" % y['Arch']
	
	# <summary>
	etree.SubElement(proot, "summary").text = y['Summary']
	# <description>
	etree.SubElement(proot, "description").text = y['Description']
	# <uservisible>
	etree.SubElement(proot, "uservisible")
	# <category>
	cat = etree.SubElement(proot, "category")
	cat.text = "Base Group"
	cat.set("lang", "en")
	# <rpm:requires>
	req = etree.SubElement(proot, "{%s}requires" %rpm_ns)
	packages = y['Packages']

	for p in packages:
		if type(p).__name__=='dict':
			a = p.values()[0]
			if a == arch:
				entry = etree.SubElement(req, "{%s}entry" %rpm_ns)
				entry.set("name", p.keys()[0])
				entry.set("arch", arch)
		else:
			entry = etree.SubElement(req, "{%s}entry" %rpm_ns)
			entry.set("name", p)
	
	return proot

def create_patterns(patterns_dir, outputdir,newobsapi):
	for f in os.listdir(patterns_dir):
		if not f.endswith('.yaml'):
			continue
		
		output_file = "%s/%s.xml" % (outputdir,os.path.basename(f).split('.')[0])
		
		print "Working on %s" % (output_file)
		
		stream = file("%s/%s" %(patterns_dir,f), 'r')
		proot = etree.Element("pattern",  nsmap=NSMAP)
		proot = process_yaml(stream,proot,newobsapi)

		# Indent the XML with xmllint and output to file.
		tree = etree.ElementTree(proot)
		tree.write("%s" % (TMP_FILE))
		os.system("xmllint --format %s --output %s" % (TMP_FILE, output_file))

def merge_patterns(patterns_dir,outputdir,newobsapi):
	xmlroot = etree.Element("patterns")
	output_file = "%s/group.xml" % (outputdir)
	count = 0
	for f in os.listdir(patterns_dir):
		if not f.endswith('.yaml'):
			continue
		print "Merging %s to %s." % (f,output_file)
		count = count + 1
		stream = file("%s/%s" %(patterns_dir,f), 'r')
		proot = etree.SubElement(xmlroot, "pattern",  nsmap=NSMAP_GROUP)
		proot = process_yaml(stream,proot,newobsapi)

	xmlroot.set('count', "%d" %count)
	tree = etree.ElementTree(xmlroot)
	# Indent the XML with xmllint and output to file.
	tree.write("%s" % (TMP_FILE))	
	os.system("xmllint --format %s --output %s" % (TMP_FILE, output_file))

if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option("", "--patternxml", action="store_true", dest="patternxml",
			default=False,
			help="Create separated pattern XML file for each pattern.")
	parser.add_option("", "--groupxml", action="store_true", dest="groupxml",
			default=False,
			help="Create merged group.xml from all the available patterns.")
	parser.add_option("-p", "--patterndir", type="string", dest="patterndir",
			default=None,
			help="Directory where the pattern .yaml files are located.")
	parser.add_option("-o", "--outputdir", type="string", dest="outputdir",
			default=".",
			help="Output directory where the resulting .xml files are created.")
	parser.add_option("", "--old-obs-xml-format", action="store_false", dest="newobsapi",
			default=True,
			help="The old OBS api isn't able to handle the newer xml format.")
	
	(options, args) = parser.parse_args()
	
	if (not options.groupxml and not options.patternxml):
		print "Error: you need to use either --patternxml or --groupxml."
		exit(1)
	
	if (not options.patterndir or not os.path.exists(options.patterndir)):
		print "Error: Pattern dir '%s' doesn't exist." % (options.patterndir)
		exit(1)

	if options.outputdir and not os.path.exists(options.outputdir):
		os.makedirs(options.outputdir)
	
	if options.patternxml:
		create_patterns(options.patterndir,options.outputdir, options.newobsapi)

	if options.groupxml:
		merge_patterns(options.patterndir,options.outputdir, options.newobsapi)
