#!/usr/bin/python

import yaml
import sys, os
import optparse
from lxml import etree

rpm_ns="http://linux.duke.edu/metadata/rpm"
pattern_ns="http://novell.com/package/metadata/suse/pattern"
NSMAP = {None : pattern_ns, "rpm": rpm_ns}

def create_patterns(patterns_dir, outputdir):

	if (not patterns_dir or not os.path.exists(patterns_dir)):
		print "Error: Pattern dir '%s' doesn't exist." % (patterns_dir)
		return

	TMP_FILE = "pattern_tmp.xml"

	for f in os.listdir(patterns_dir):
		if not f.endswith('.yaml'):
			continue
		
		output_file = "%s/%s.xml" % (outputdir,os.path.basename(f).split('.')[0])
		
		print "Working on %s" % (output_file)
		
		stream = file("%s/%s" %(patterns_dir,f), 'r')
		y = yaml.load(stream)        
		proot = etree.Element("pattern",  nsmap=NSMAP)
		# <name>
		etree.SubElement(proot, "name").text = y['Name']
		
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
		# <???>
		req = etree.SubElement(proot, "{%s}requires" %rpm_ns)
		if y.has_key('Patterns'):
			collect = []
			for pat in y['Patterns']:
				if os.path.exists("%s/%s.yaml" %(patterns_dir, pat)):
					pf = file("%s/%s.yaml" %(patterns_dir, pat), 'r')
					pfy = yaml.load(pf)
				if pfy.has_key('Packages'):
					collect += pfy['Packages']
		elif y.has_key('Packages'):
			collect = y['Packages']

		for p in collect:
			if type(p).__name__=='dict':
				a = p.values()[0]
				if a == arch:
					entry = etree.SubElement(req, "{%s}entry" %rpm_ns)
				entry.set("name", p.keys()[0])
				entry.set("arch", arch)
		else:
			entry = etree.SubElement(req, "{%s}entry" %rpm_ns)
			entry.set("name", p)
			
		if outputdir and not os.path.exists(outputdir):
			os.makedirs(outputdir)

		tree = etree.ElementTree(proot)
		tree.write("%s" % (TMP_FILE))
		os.system("xmllint --format %s --output %s" % (TMP_FILE, output_file))


if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option("-p", "--patterndir", type="string", dest="patterndir",
			default=None,
			help="Directory where the pattern .yaml files are located.")
	parser.add_option("-o", "--outputdir", type="string", dest="outputdir",
			default=None,
			help="Output directory where the resulting .xml files are created.")
		
	(options, args) = parser.parse_args()

	create_patterns(options.patterndir,options.outputdir)

