import re, os, sys, string
import datetime
import getopt
import getpass

version = "1.0.2"

lines = ""
iesDefs = {}
ieofielist = {}
outdir = './'

filenames = []
verbosity = 0
prefix = ""

FAIL = '\033[91m'
WARN = '\033[93m'
ENDC = '\033[0m'

fileprefix = ""
fileprefix_first_upper = ""

def printFail(string):
    sys.stderr.write(FAIL + string + ENDC + "\n")

def printWarning(string):
    print WARN + string + ENDC

def printDebug(string):
    if verbosity > 0:
        print string

def outputHeaderToFile(f, filename):
    now = datetime.datetime.now()
    f.write("""/*******************************************************************************

  Eurecom OpenAirInterface
  Copyright(c) 1999 - 2015 Eurecom

  This program is free software; you can redistribute it and/or modify it
  under the terms and conditions of the GNU General Public License,
  version 2, as published by the Free Software Foundation.

  This program is distributed in the hope it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
  more details.

  You should have received a copy of the GNU General Public License along with
  this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.

  The full GNU General Public License is included in this distribution in
  the file called "COPYING".

  Contact Information
  Openair Admin: openair_admin@eurecom.fr
  Openair Tech : openair_tech@eurecom.fr
  Forums       : http://forums.eurecom.fr/openairinterface
  Address      : EURECOM, Campus SophiaTech, 450 Route des Chappes
                 06410 Biot FRANCE

*******************************************************************************/

""")
    f.write("/*******************************************************************************\n")
    f.write(" * This file had been created by asn1tostruct.py script v%s\n" % (version))
    f.write(" * Please do not modify this file but regenerate it via script.\n")
    f.write(" * Created on: %s by %s\n * from %s\n" % (str(now), getpass.getuser(), filenames))
    f.write(" ******************************************************************************/\n")

def lowerFirstCamelWord(word):
    """ puts the first word in a CamelCase Word in lowercase.

    I.e. CustomerID becomes customerID, XMLInfoTest becomes xmlInfoTest
    """
    newstr = ''
    swapped = word.swapcase()
    idx = 0

    # if it's all-caps, return an all-lowered version
    lowered = word.lower()

    if swapped == lowered:
        return lowered

    for c in swapped:
        if c in string.lowercase:
            newstr += c
            idx    += 1
        else:
            break
    if idx < 2:
        newstr += word[idx:]
    else:
        newstr = newstr[:-1]+ word[idx-1:]

    return newstr

def usage():
    print "Python parser for asn1 v%s" % (version)
    print "Usage: python asn1tostruct.py [options]"
    print "Available options:"
    print "-d        Enable script debug"
    print "-f [file] Input file to parse"
    print "-o [dir]  Output files to given directory"
    print "-h        Print this help and return"

try:
    opts, args = getopt.getopt(sys.argv[1:], "df:ho:", ["debug", "file", "help", "outdir"])
except getopt.GetoptError as err:
    # print help information and exit:
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ("-f", "--file"):
        filenames.append(a)
    if o in ("-d", "--debug"):
        verbosity = 1
    if o in ("-o", "--outdir"):
        outdir = a
        if outdir.rfind('/') != len(outdir):
            outdir += '/'
    if o in ("-h", "--help"):
        usage()
        sys.exit(2)

for filename in filenames:
    file = open(filename, 'r')
    for line in file:
        # Removing any comment
        if line.find('--') >= 0:
            line = line[:line.find('--')]
        # Removing any carriage return
        lines += re.sub('\r', '', line)

    for m in re.findall(r'([a-zA-Z0-9-]+)\s*::=\s+SEQUENCE\s+\(\s*SIZE\s*\(\s*\d+\s*\.\.\s*[0-9a-zA-Z-]+\s*\)\s*\)\s*OF\s+[a-zA-Z-]+\s*\{\s*\{\s*([0-9a-zA-Z-]+)\s*\}\s*\}', lines, re.MULTILINE):
        ieofielist[m[0]] = m[1]
    for m in re.findall(r'([a-zA-Z0-9-]+)\s*::=\s+E-RAB-IE-ContainerList\s*\{\s*\{\s*([a-zA-Z0-9-]+)\s*\}\s*\}', lines, re.MULTILINE):
        ieofielist[m[0]] = m[1]

    for i in re.findall(r'([a-zA-Z0-9-]+)\s+([A-Z0-9-]+)\s*::=\s*\{\s+([\,\|\{\}\t\n\.{3}\ \-a-zA-Z0-9]+)\s+}\n', lines, re.MULTILINE):
        ies = []
        maxLength = 0
        # TODO: handle extensions
        if i[1].find('EXTENSION') >= 0:
            continue
        if fileprefix == "":
            fileprefix = i[1][:i[1].find('-')].lower()
        for j in re.findall(r'\s*\{\s*([a-zA-Z0-9-\ \t]+)\s*\}\s*[\|,]*', i[2], re.MULTILINE):
            for k in re.findall(r'ID\s*([a-zA-Z0-9\-]+)\s*CRITICALITY\s*([a-zA-Z0-9\-]+)\s+[A-Z]+\s+([a-zA-Z0-9\-]+)\s*PRESENCE\s*([a-zA-Z0-9\-]+)', j, re.MULTILINE):
                printDebug("Got new ie for message " + i[0] + ": " + str(k))
                if len(k[2]) > maxLength:
                    maxLength = len(k[2])
                ies.append(k)

        if len(ies) > 0:
            iesDefs[i[0]] = { "length": maxLength, "ies": ies }
        else:
            printWarning("Didn't find any information element for message: " + i[0])

if len(iesDefs) == 0:
    printFail("No Information Element parsed, exiting")
    sys.exit(0)

fileprefix_first_upper = fileprefix[0].upper() + fileprefix[1:]

f = open(outdir + fileprefix + '_ies_defs.h', 'w')
outputHeaderToFile(f, filename)
f.write("#include \"%s_common.h\"\n\n" % (fileprefix))
f.write("#ifndef %s_IES_DEFS_H_\n#define %s_IES_DEFS_H_\n\n" % (fileprefix.upper(), fileprefix.upper()))
f.write("/* Define the version of script used to generate this file */\n")
f.write("#define %s_SCRIPT_VERSION (%s)\n\n" % (fileprefix.upper(), re.sub('\.', '', version)))

for key in iesDefs:

    if key not in ieofielist.values():
        continue

    for (i, j) in ieofielist.items():
        if j == key:
            break

    f.write("typedef struct %sIEs_s {\n" % (re.sub('-', '_', i)))
    f.write("    A_SEQUENCE_OF(struct %s_s) %s;\n" % (re.sub('IEs', '', re.sub('-', '_', ieofielist[i])), lowerFirstCamelWord(re.sub('IEs', '', re.sub('-', '_', ieofielist[i])))))
    f.write("} %sIEs_t;\n\n" % (re.sub('-', '_', i)))

for key in iesDefs:
    keyupperunderscore = re.sub('-', '_', key.upper())
    keylowerunderscore = re.sub('-', '_', key.lower())
    shift = 0

    if len(iesDefs[key]["ies"]) == 0:
        continue

    # Presence mask
    for ie in iesDefs[key]["ies"]:
        ieupperunderscore = re.sub('-', '_', re.sub('id-', '', ie[0])).upper()

        if ie[3] == "optional" or ie[3] == "conditional":
            f.write("#define {0:<{pad}} {1}\n".format("%s_%s_PRESENT" % (keyupperunderscore, ieupperunderscore), "(1 << %d)" % shift,
            pad=iesDefs[key]["length"] + len(keyupperunderscore) + 9))
            shift += 1
    if (shift > 0):
        f.write("\n")

    f.write("typedef struct %s_s {\n" % (re.sub('-', '_', key)))
    if (shift > 0):
        f.write("    {0:<{pad}} {1};\n".format("uint16_t", "presenceMask", pad=iesDefs[key]["length"] + 2))
    for ie in iesDefs[key]["ies"]:
        ieunderscore = re.sub('-', '_', ie[2])
        iename = re.sub('id-', '', ie[0])
        ienameunderscore = lowerFirstCamelWord(re.sub('-', '_', iename))
        if ie[2] in ieofielist:
            f.write("    %sIEs_t %s;" % (re.sub('-', '_', ie[2]), ienameunderscore))
        else:
            f.write("    {0:<{pad}} {1};".format("%s_t" % ieunderscore, ienameunderscore, pad=iesDefs[key]["length"] + 2))
        if ie[3] == "optional":
            f.write(" ///< Optional field")
        elif ie[3] == "conditional":
            f.write(" ///< Conditional field")
        f.write("\n")

    f.write("} %s_t;\n\n" % (re.sub('-', '_', key)))

f.write("typedef struct %s_message_s {\n" % (fileprefix))
f.write("    %s_ProcedureCode_t procedureCode;\n" % (fileprefix_first_upper))
f.write("    %s_Criticality_t   criticality;\n" % (fileprefix_first_upper))
f.write("    uint8_t            direction;\n")
f.write("    union {\n")

messageList = iesDefs.keys()
messageList.sort()
for message in messageList:
    if message in ieofielist.values():
        continue
    if len(iesDefs[message]["ies"]) == 0:
        continue
    f.write("        %s_t %s;\n" % (re.sub('-', '_', message), lowerFirstCamelWord(re.sub('-', '_', message))))
f.write("    } msg;\n")
f.write("} %s_message;\n\n" % (fileprefix))

for key in iesDefs:
    if key in ieofielist.values():
        continue
    structName = re.sub('ies', '', key)
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', re.sub('-IEs', '', key)))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    keylowerunderscore = re.sub('-', '_', key.lower())
    firstlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    f.write("/* %s in iesDefs not in ieofielist.values()  */\n" % (key))
    f.write("/** \\brief Decode function for %s ies.\n" % (key))
    if len(iesDefs[key]["ies"]) != 0:
        f.write(" * \\param %s Pointer to ASN1 structure in which data will be stored\n" % (lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write(" *  \\param any_p Pointer to the ANY value to decode.\n")
    f.write(" **/\n")
    f.write("int %s_decode_%s(\n" % (fileprefix, keylowerunderscore))
    if len(iesDefs[key]["ies"]) != 0:
        f.write("    %s_t *%s,\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write("    ANY_t *any_p);\n\n")

    f.write("/* %s in iesDefs not in ieofielist.values()  */\n" % (key))
    f.write("/** \\brief Compare function for %s ies.\n" % (key))
    f.write(" *  \\param %s Pointer to the ASN1 structure.\n" % (firstlower))
    f.write(" *  \\param %s Pointer to the ASN1 structure.\n" % (firstlower))
    f.write(" **/\n")
    f.write("asn_comp_rval_t *  %s_compare_%s(\n" % (fileprefix, keylowerunderscore))
    f.write("    %s_t *%s1,\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write("    %s_t *%s2);\n\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))

    if len(iesDefs[key]["ies"]) == 0:
        continue

    f.write("/* %s in iesDefs not in ieofielist.values()  */\n" % (key))
    f.write("/** \\brief Encode function for %s ies.\n" % (key))
    f.write(" *  \\param %s Pointer to the ASN1 structure.\n" % (firstlower))
    f.write(" *  \\param %s Pointer to the IES structure.\n" % (lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write(" **/\n")
    f.write("int %s_encode_%s(\n" % (fileprefix, re.sub('-', '_', structName.lower())))
    f.write("    %s_t *%s,\n" % (asn1cStruct, firstlower))
    f.write("    %s_t *%s);\n\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))


for key in iesDefs:
    if key not in ieofielist.values():
        continue
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', key))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    firstlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))
    f.write("/* %s in iesDefs in ieofielist.values()  */\n" % (key))
    f.write("/** \\brief Encode function for %s ies.\n" % (key))
    f.write(" *  \\param %s Pointer to the ASN1 structure.\n" % (firstlower))
    f.write(" *  \\param %s Pointer to the IES structure.\n" % (lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write(" **/\n")
    f.write("/* %s in iesDefs in ieofielist.values()  */\n" % (key))
    f.write("int %s_encode_%s(\n" % (fileprefix, firstlower.lower()))
    f.write("    %s_t *%s,\n" % (asn1cStruct, firstlower))
    f.write("    %sIEs_t *%sIEs);\n\n" % (asn1cStruct, firstlower))
    f.write("/** \\brief Decode function for %s ies.\n" % (key))
    f.write(" *  \\param any_p Pointer to the ANY value to decode.\n")
    f.write(" *  \\param callback Callback function called when any_p is successfully decoded.\n")
    f.write(" **/\n")
    f.write("/* %s in iesDefs in ieofielist.values()  */\n" % (key))
    f.write("int %s_decode_%s(\n" % (fileprefix, firstlower.lower()))
    f.write("    %sIEs_t *%sIEs,\n" % (asn1cStruct, firstlower))
    f.write("    %s_t *%s);\n\n" % (asn1cStruct, lowerFirstCamelWord(asn1cStruct)))
    f.write("/** \\brief Compare function for %s ies.\n" % (key))
    f.write(" *  \\param %s Pointer to the IES structure.\n" % (firstlower))
    f.write(" *  \\param %s Pointer to the IES structure.\n" % (firstlower))
    f.write(" **/\n")
    f.write("asn_comp_rval_t *  %s_compare_%s(\n" % (fileprefix, firstlower.lower()))
    f.write("    %sIEs_t *%s1,\n"    % (asn1cStruct, firstlower))
    f.write("    %sIEs_t *%s2);\n\n" % (asn1cStruct, firstlower))



for key in iesDefs:
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', key))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    firstlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    if key in ieofielist.values():
        f.write("/** \\brief Display %s encapsulated IE using XER encoding.\n" % (asn1cStruct))
        f.write(" *  \\param %s Pointer to the IES structure.\n" % (lowerFirstCamelWord(re.sub('-', '_', key))))
        f.write(" *  \\param file File descriptor to write output.\n")
        f.write(" **/\n")
        f.write("asn_enc_rval_t %s_xer_print_%s(\n" % (fileprefix, re.sub('item', 'list', firstlower.lower())))
        f.write("    asn_app_consume_bytes_f *cb,\n")
        f.write("    void *app_key,\n")
        f.write("    %sIEs_t *%sIEs);\n\n" % (re.sub('item', 'list', asn1cStruct), firstlower))
    else:
        f.write("/** \\brief Display %s message using XER encoding.\n" % (asn1cStruct))
        f.write(" *  \\param message_p Pointer to root message.\n")
        f.write(" *  \\param file File descriptor to write output.\n")
        f.write(" **/\n")
        f.write("asn_enc_rval_t %s_xer_print_%s(\n" % (fileprefix, firstlower.lower()))
        f.write("    asn_app_consume_bytes_f *cb,\n")
        f.write("    void *app_key,\n")
        f.write("    %s_message *message_p);\n\n" % (fileprefix))

f.write("int %s_xer__print2sp(const void *buffer, size_t size, void *app_key);\n\n" % (fileprefix.lower()))
f.write("int %s_xer__print2fp(const void *buffer, size_t size, void *app_key);\n\n" % (fileprefix.lower()))
f.write("extern size_t %s_string_total_size;\n\n" % (fileprefix.lower()))
f.write("#endif /* %s_IES_DEFS_H_ */\n\n" % (fileprefix.upper()))

#Generate Decode functions
f = open(outdir + fileprefix + '_decoder.c', 'w')
outputHeaderToFile(f, filename)
f.write("#include \"%s_common.h\"\n#include \"%s_ies_defs.h\"\n\n" % (fileprefix, fileprefix))
for key in iesDefs:
    if key in ieofielist.values():
        continue
    structName = re.sub('ies', '', key)
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', key))
    if asn1cStruct.rfind('_') == len(asn1cStruct) - 1:
        asn1cStruct = asn1cStruct[:-1]
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    ielistname = re.sub('UE', 'ue', asn1cStruct)
    ielistnamefirstlower = ielistname[:1].lower() + ielistname[1:]
    asn1cStructfirstlower = asn1cStruct[:1].lower() + asn1cStruct[1:]
    keyName = re.sub('-', '_', key)
    keyupperunderscore = keyName.upper()
    firstlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    iesaccess = ""
    if key not in ieofielist.values():
        iesaccess = "%s_ies." % (firstlower)

    f.write("int %s_decode_%s(\n" % (fileprefix, re.sub('-', '_', structName.lower())))
    if len(iesDefs[key]["ies"]) != 0:
        f.write("    %s_t *%s,\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write("    ANY_t *any_p) {\n\n")

    f.write("    %s_t  %s;\n    %s_t *%s_p = &%s;\n" % (asn1cStruct, asn1cStructfirstlower, asn1cStruct, asn1cStructfirstlower, asn1cStructfirstlower))
    f.write("    int i, decoded = 0;\n")
    if len(iesDefs[key]["ies"]) != 0:
        f.write("    int tempDecoded = 0;\n")

    f.write("    assert(any_p != NULL);\n")
    if len(iesDefs[key]["ies"]) != 0:
        f.write("    assert(%s != NULL);\n\n" % (lowerFirstCamelWord(re.sub('-', '_', key))))

    f.write("    %s_DEBUG(\"Decoding message %s (%%s:%%d)\\n\", __FILE__, __LINE__);\n\n" % (fileprefix.upper(), re.sub('-', '_', keyName)))
    f.write("    ANY_to_type_aper(any_p, &asn_DEF_%s, (void**)&%s_p);\n\n" % (asn1cStruct, asn1cStructfirstlower))
    f.write("    for (i = 0; i < %s_p->%slist.count; i++) {\n" % (asn1cStructfirstlower, iesaccess))
    f.write("        %s_IE_t *ie_p;\n" % (fileprefix[0].upper() + fileprefix[1:]))
    f.write("        ie_p = %s_p->%slist.array[i];\n" % (asn1cStructfirstlower, iesaccess))
    f.write("        switch(ie_p->id) {\n")
    for ie in iesDefs[key]["ies"]:
        iename = re.sub('id-', '', ie[0])
        ienameunderscore = lowerFirstCamelWord(re.sub('-', '_', iename))
        ienameunderscorefirstlower = lowerFirstCamelWord(ienameunderscore)
        ietypesubst = re.sub('-', '', ie[2])
        ietypeunderscore = re.sub('-', '_', ie[2])
        ieupperunderscore = re.sub('-', '_', re.sub('id-', '', ie[0])).upper()

        if ie[3] == "optional":
            f.write("            /* Optional field */\n")
        elif ie[3] == "conditional":
            f.write("            /* Conditional field */\n")
        f.write("            case %s_ProtocolIE_ID_%s:\n" % (fileprefix_first_upper, re.sub('-', '_', ie[0])))
        f.write("            {\n")
        f.write("                %s_t *%s_p = NULL;\n" % (ietypeunderscore, lowerFirstCamelWord(ietypesubst)))
        if ie[3] != "mandatory":
            f.write("                %s->presenceMask |= %s_%s_PRESENT;\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), keyupperunderscore, ieupperunderscore))
        f.write("                tempDecoded = ANY_to_type_aper(&ie_p->value, &asn_DEF_%s, (void**)&%s_p);\n" % (ietypeunderscore, lowerFirstCamelWord(ietypesubst)))
        f.write("                if (tempDecoded < 0 || %s_p == NULL) {\n" % (lowerFirstCamelWord(ietypesubst)))
        f.write("                    %s_ERROR(\"Decoding of IE %s failed\\n\");\n" % (fileprefix.upper(), ienameunderscore))
        f.write("                    if (%s_p)\n" % (lowerFirstCamelWord(ietypesubst)))
        f.write("                        ASN_STRUCT_FREE(asn_DEF_%s, %s_p);\n" % (ietypeunderscore, lowerFirstCamelWord(ietypesubst)))
        f.write("                    return -1;\n")
        f.write("                }\n")
        f.write("                decoded += tempDecoded;\n")
        f.write("                if (asn1_xer_print)\n")
        f.write("                    xer_fprint(stdout, &asn_DEF_%s, %s_p);\n" % (ietypeunderscore, lowerFirstCamelWord(ietypesubst)))
        if ie[2] in ieofielist.keys():
            f.write("                if (%s_decode_%s(&%s->%s, %s_p) < 0) {\n" % (fileprefix, ietypeunderscore.lower(), lowerFirstCamelWord(re.sub('-', '_', key)), ienameunderscore, lowerFirstCamelWord(ietypesubst)))
            f.write("                    %s_ERROR(\"Decoding of encapsulated IE %s failed\\n\");\n" % (fileprefix.upper(), lowerFirstCamelWord(ietypesubst)))
            f.write("                    ASN_STRUCT_FREE(asn_DEF_%s, %s_p);\n" % (ietypeunderscore, lowerFirstCamelWord(ietypesubst)))
            f.write("                }\n")
        else:
            f.write("                memcpy(&%s->%s, %s_p, sizeof(%s_t));\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), ienameunderscore, lowerFirstCamelWord(ietypesubst), ietypeunderscore))
            #f.write("                ASN_STRUCT_FREE(asn_DEF_%s, %s_p);\n" % (ietypeunderscore, lowerFirstCamelWord(ietypesubst)))
        f.write("            } break;\n")
    f.write("            default:\n")
    f.write("                %s_ERROR(\"Unknown protocol IE id (%%d) for message %s\\n\", (int)ie_p->id);\n" % (fileprefix.upper(), re.sub('-', '_', structName.lower())))
    f.write("                return -1;\n")
    f.write("        }\n")
    f.write("    }\n")
    f.write("    return decoded;\n")
    f.write("}\n\n")

for key in iesDefs:
    if key not in ieofielist.values():
        continue

    keyname = re.sub('IEs', '', re.sub('Item', 'List', key))

    f.write("int %s_decode_%s(\n" % (fileprefix, re.sub('-', '_', keyname).lower()))
    f.write("    %sIEs_t *%sIEs,\n" % (re.sub('-', '_', keyname), lowerFirstCamelWord(re.sub('-', '_', keyname))))
    f.write("    %s_t *%s) {\n\n" % (re.sub('-', '_', keyname), lowerFirstCamelWord(re.sub('-', '_', keyname))))
    f.write("    int i, decoded = 0;\n")
    f.write("    int tempDecoded = 0;\n\n")

    f.write("    assert(%s != NULL);\n" % (lowerFirstCamelWord(re.sub('-', '_', keyname))));
    f.write("    assert(%sIEs != NULL);\n\n" % (lowerFirstCamelWord(re.sub('-', '_', keyname))));

    f.write("    for (i = 0; i < %s->list.count; i++) {\n" % (lowerFirstCamelWord(re.sub('-', '_', keyname))))
    f.write("        %s_IE_t *ie_p = %s->list.array[i];\n" % (fileprefix[0].upper() + fileprefix[1:], lowerFirstCamelWord(re.sub('-', '_', keyname))))
    f.write("        switch (ie_p->id) {\n")
    for ie in iesDefs[key]["ies"]:
        iename = re.sub('id-', '', ie[0])
        ienameunderscore = lowerFirstCamelWord(re.sub('-', '_', iename))
        f.write("            case %s_ProtocolIE_ID_%s:\n" % (fileprefix_first_upper, re.sub('-', '_', ie[0])))
        f.write("            {\n")
        f.write("                %s_t *%s_p = NULL;\n" % (re.sub('-', '_', ie[2]), lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("                tempDecoded = ANY_to_type_aper(&ie_p->value, &asn_DEF_%s, (void**)&%s_p);\n" % (re.sub('-', '_', ie[2]), lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("                if (tempDecoded < 0 || %s_p == NULL) {\n" % (lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("                    %s_ERROR(\"Decoding of IE %s for message %s failed\\n\");\n" % (fileprefix.upper(), ienameunderscore, re.sub('-', '_', keyname)))
        f.write("                    if (%s_p)\n" % (lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        #f.write("                        free(%s_p);\n" % (lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("                        ASN_STRUCT_FREE(asn_DEF_%s, %s_p);\n" % (re.sub('-', '_', ie[2]), lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("                    return -1;\n")
        f.write("                }\n")
        f.write("                decoded += tempDecoded;\n")
        f.write("                if (asn1_xer_print)\n")
        f.write("                    xer_fprint(stdout, &asn_DEF_%s, %s_p);\n" % (re.sub('-', '_', ie[2]), lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("                ASN_SEQUENCE_ADD(&%sIEs->%s, %s_p);\n" % (lowerFirstCamelWord(re.sub('-', '_', keyname)),
        re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key))), lowerFirstCamelWord(re.sub('-', '', ie[2]))))
        f.write("            } break;\n")
    f.write("            default:\n")
    f.write("                %s_ERROR(\"Unknown protocol IE id (%%d) for message %s\\n\", (int)ie_p->id);\n" % (fileprefix.upper(), re.sub('-', '_', structName.lower())))
    f.write("                return -1;\n")
    f.write("        }\n")
    f.write("    }\n")
    f.write("    return decoded;\n")
    f.write("}\n\n")


#Generate IES Encode functions
f = open(outdir + fileprefix + '_encoder.c', 'w')
outputHeaderToFile(f,filename)
f.write("#include \"%s_common.h\"\n" % (fileprefix))
f.write("#include \"%s_ies_defs.h\"\n\n" % (fileprefix))
for key in iesDefs:
    if key in ieofielist.values():
        continue

    structName = re.sub('ies', '', key)
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', key))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    if asn1cStruct.rfind('_') == len(asn1cStruct) - 1:
        asn1cStruct = asn1cStruct[:-1]
    asn1cStructfirstlower = asn1cStruct[:1].lower() + asn1cStruct[1:]
    firstwordlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    iesaccess = ""
    if key not in ieofielist.values():
        iesaccess = "%s_ies." % (firstwordlower)

    keyName = re.sub('-', '_', key)
    keyupperunderscore = keyName.upper()
    # No IE to encode...
    if len(iesDefs[key]["ies"]) == 0:
        continue

    f.write("int %s_encode_%s(\n" % (fileprefix, re.sub('-', '_', structName.lower())))
    f.write("    %s_t *%s,\n" % (asn1cStruct, firstwordlower))
    f.write("    %s_t *%s) {\n\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))

    f.write("    %s_IE_t *ie;\n\n" % (fileprefix_first_upper))

    f.write("    assert(%s != NULL);\n" % (firstwordlower));
    f.write("    assert(%s != NULL);\n\n" % (lowerFirstCamelWord(re.sub('-', '_', key))));

    for ie in iesDefs[key]["ies"]:
        iename = re.sub('-', '_', re.sub('id-', '', ie[0]))
        ienameunderscore = re.sub('-', '_', iename)
        ienamefirstwordlower = lowerFirstCamelWord(iename)
        ieupperunderscore = re.sub('-', '_', re.sub('id-', '', ie[0])).upper()
        ietypeunderscore = re.sub('-', '_', ie[2])

        if ie[3] != "mandatory":
            if ie[3] == "optional":
                f.write("    /* Optional field */\n")
            elif ie[3] == "conditional":
                f.write("    /* Conditional field */\n")
            f.write("    if (%s->presenceMask & %s_%s_PRESENT) {\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), keyupperunderscore, ieupperunderscore))
            #f.write("        == %s_%s_PRESENT) {\n" % (keyupperunderscore, ieupperunderscore))
            f.write("        if ((ie = %s_new_ie(%s_ProtocolIE_ID_%s,\n" % (fileprefix, fileprefix_first_upper, re.sub('-', '_', ie[0])))
            f.write("                            %s_Criticality_%s,\n" % (fileprefix_first_upper, ie[1]))
            f.write("                            &asn_DEF_%s,\n" % (ietypeunderscore))
            f.write("                            &%s->%s)) == NULL) {\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower))
            f.write("            return -1;\n")
            f.write("        }\n")
            f.write("        ASN_SEQUENCE_ADD(&%s->%slist, ie);\n" % (firstwordlower, iesaccess))
            f.write("    }\n\n")
        else:
            if ie[2] in ieofielist.keys():
                f.write("    %s_t %s;\n\n" % (ietypeunderscore, ienamefirstwordlower))
                f.write("    memset(&%s, 0, sizeof(%s_t));\n" % (ienamefirstwordlower, ietypeunderscore))
                f.write("\n")
                f.write("    if (%s_encode_%s(&%s, &%s->%s) < 0) return -1;\n" % (fileprefix, ietypeunderscore.lower(), ienamefirstwordlower, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower))
            f.write("    if ((ie = %s_new_ie(%s_ProtocolIE_ID_%s,\n" % (fileprefix, fileprefix_first_upper, re.sub('-', '_', ie[0])))
            f.write("                        %s_Criticality_%s,\n" % (fileprefix_first_upper, ie[1]))
            f.write("                        &asn_DEF_%s,\n" % (ietypeunderscore))
            if ie[2] in ieofielist.keys():
                f.write("                          &%s)) == NULL) {\n" % (ienamefirstwordlower))
            else:
                f.write("                          &%s->%s)) == NULL) {\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower))
            f.write("        return -1;\n")
            f.write("    }\n")
            f.write("    ASN_SEQUENCE_ADD(&%s->%slist, ie);\n\n" % (firstwordlower, iesaccess))
            if ie[2] in ieofielist.keys():
                f.write("    /* Free any dynamic allocation that is no more used */\n")
                f.write("    ASN_STRUCT_FREE_CONTENTS_ONLY(asn_DEF_%s, &%s);\n\n" % (ietypeunderscore, ienamefirstwordlower))

    f.write("    return 0;\n")
    f.write("}\n\n")

for (key, value) in iesDefs.items():
    if key not in ieofielist.values():
        continue

    ie = value["ies"][0]
    ietypeunderscore = re.sub('-', '_', ie[2])
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', re.sub('-IEs', '', key)))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    firstwordlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    for (i, j) in ieofielist.items():
        if j == key:
            break
    f.write("int %s_encode_%s(\n" % (fileprefix, re.sub('-', '_', i).lower()))
    f.write("    %s_t *%s,\n" % (asn1cStruct, firstwordlower))
    f.write("    %sIEs_t *%sIEs) {\n\n" % (re.sub('-', '_', i), lowerFirstCamelWord(re.sub('-', '_', i))))
    f.write("    int i;\n")

    f.write("    %s_IE_t *ie;\n\n" % (fileprefix_first_upper))

    f.write("    assert(%s != NULL);\n" % (firstwordlower));
    f.write("    assert(%sIEs != NULL);\n\n" % (lowerFirstCamelWord(re.sub('-', '_', i))));

    f.write("    for (i = 0; i < %sIEs->%s.count; i++) {\n" % (firstwordlower, re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
    f.write("        if ((ie = %s_new_ie(%s_ProtocolIE_ID_%s,\n" % (fileprefix, fileprefix_first_upper, re.sub('-', '_', ie[0])))
    f.write("                            %s_Criticality_%s,\n" % (fileprefix_first_upper, ie[1]))
    f.write("                            &asn_DEF_%s,\n" % (ietypeunderscore))
    f.write("                            %sIEs->%s.array[i])) == NULL) {\n" % (firstwordlower, re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
    f.write("            return -1;\n")
    f.write("        }\n")
    f.write("        ASN_SEQUENCE_ADD(&%s->list, ie);\n" % (firstwordlower))
    f.write("    }\n")
    f.write("    return 0;\n")
    f.write("}\n\n")

#Generate xer print functions
f = open(outdir + fileprefix + '_xer_print.c', 'w')
outputHeaderToFile(f, filename)
f.write("#include <stdlib.h>\n")
f.write("#include <stdio.h>\n\n")
f.write("#include <asn_application.h>\n#include <asn_internal.h>\n\n")
f.write("#include \"%s_common.h\"\n#include \"%s_ies_defs.h\"\n\n" % (fileprefix, fileprefix))

f.write("size_t %s_string_total_size = 0;\n\n" % (fileprefix.lower()))
f.write("""int
%s_xer__print2fp(const void *buffer, size_t size, void *app_key) {
    FILE *stream = (FILE *)app_key;

    if(fwrite(buffer, 1, size, stream) != size)
        return -1;

    return 0;
}

""" % (fileprefix.lower()))

f.write("""int %s_xer__print2sp(const void *buffer, size_t size, void *app_key) {
    char *string = (char *)app_key;

    /* Copy buffer to the formatted string */
    memcpy(&string[%s_string_total_size], buffer, size);

    %s_string_total_size += size;

    return 0;
}

""" % (fileprefix.lower(), fileprefix.lower(), fileprefix.lower()))

f.write("""static asn_enc_rval_t
xer_encode_local(asn_TYPE_descriptor_t *td, void *sptr,
        asn_app_consume_bytes_f *cb, void *app_key, int indent) {
    asn_enc_rval_t er, tmper;
    const char *mname;
    size_t mlen;
    int xcan = 2;

    if(!td || !sptr) goto cb_failed;

    mname = td->xml_tag;
    mlen = strlen(mname);

    _i_ASN_TEXT_INDENT(0, indent);
    _ASN_CALLBACK3("<", 1, mname, mlen, ">", 1);

    tmper = td->xer_encoder(td, sptr, indent + 1, XER_F_BASIC, cb, app_key);
    if(tmper.encoded == -1) return tmper;

    _ASN_CALLBACK3("</", 2, mname, mlen, ">\\n", xcan);

    er.encoded = 4 + xcan + (2 * mlen) + tmper.encoded;

    _ASN_ENCODED_OK(er);
cb_failed:
    _ASN_ENCODE_FAILED;
}
""")

for (key, value) in iesDefs.items():
    keyName = re.sub('-', '_', key)
    keyupperunderscore = keyName.upper()
    iesStructName = lowerFirstCamelWord(re.sub('-', '_', key))

    ie = value["ies"][0]
    ietypeunderscore = re.sub('-', '_', ie[2])

    if key in ieofielist.values():
        f.write("asn_enc_rval_t %s_xer_print_%s(\n" % (fileprefix, re.sub('ies', '', re.sub('item', 'list', re.sub('-', '_', key).lower()))))
    else:
        f.write("asn_enc_rval_t %s_xer_print_%s(\n" % (fileprefix, re.sub('ies', '', re.sub('-', '_', key).lower())))
    #f.write("    FILE *file,\n")
    f.write("    asn_app_consume_bytes_f *cb,\n")
    f.write("    void *app_key,\n")
    if key in ieofielist.values():
        iesStructName = lowerFirstCamelWord(re.sub('Item', 'List', re.sub('-', '_', key)))
        f.write("    %sIEs_t *%s) {\n\n" % (re.sub('IEs', '', re.sub('Item', 'List', re.sub('-', '_', key))), iesStructName))
        f.write("    int i;\n")
        f.write("    asn_enc_rval_t er;\n")
    else:
        f.write("    %s_message *message_p)\n{\n" % (fileprefix))
        f.write("    %s_t *%s;\n" % (re.sub('-', '_', key), iesStructName))
        f.write("    asn_enc_rval_t er;\n")
        #f.write("    void *app_key = (void *)file;\n")
        #f.write("    asn_app_consume_bytes_f *cb = %s_xer__print2fp;\n\n" % (fileprefix.lower()))

        f.write("    %s = &message_p->msg.%s;\n\n" % (iesStructName, iesStructName))

    if key in ieofielist.values():
        # Increase indentation level
        f.write("    for (i = 0; i < %s->%s.count; i++) {\n" % (iesStructName, re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
        #f.write("        xer_fprint(file, &asn_DEF_%s, %s->%s.array[i]);\n" % (ietypeunderscore, iesStructName, re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
        f.write("        er = xer_encode(&asn_DEF_%s, %s->%s.array[i], XER_F_BASIC, cb, app_key);\n" % (ietypeunderscore, iesStructName, re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
        f.write("    }\n")
    else:
        f.write("    cb(\"<%s-PDU>\\n\", %d, app_key);\n" % (key, len("<%s-PDU>\n" % (key))))
        f.write("    xer_encode_local(&asn_DEF_%s_Criticality, &message_p->criticality, cb, app_key, 1);\n" % fileprefix_first_upper)
        f.write("    xer_encode_local(&asn_DEF_%s_ProcedureCode, &message_p->procedureCode, cb, app_key, 1);\n" % fileprefix_first_upper)

        f.write("    cb(\"    <%s>\\n\", %d, app_key);\n" % (key, len("    <%s>\n" % (key))))

        for ie in iesDefs[key]["ies"]:
            iename = re.sub('-', '_', re.sub('id-', '', ie[0]))
            ienameunderscore = re.sub('-', '_', iename)
            ienamefirstwordlower = lowerFirstCamelWord(iename)
            ietypeunderscore = re.sub('-', '_', ie[2])
            ieupperunderscore = re.sub('-', '_', re.sub('id-', '', ie[0])).upper()

            if ie[3] != "mandatory":
                if ie[3] == "optional":
                    f.write("    /* Optional field */\n")
                elif ie[3] == "conditional":
                    f.write("    /* Conditional field */\n")
                f.write("    if (%s->presenceMask & %s_%s_PRESENT)\n    " % (iesStructName, keyupperunderscore, ieupperunderscore))

            # Is it an encapsulated IE ?
            if ie[2] in ieofielist.keys():
                f.write("    %s_xer_print_%s(cb, app_key, &%s->%s);\n" % (fileprefix, re.sub('ies', '', re.sub('-', '_', ie[2]).lower()), iesStructName, ienamefirstwordlower))
            else:
                f.write("    xer_encode_local(&asn_DEF_%s, &%s->%s, cb, app_key, 2);\n" % (ietypeunderscore, iesStructName, ienamefirstwordlower))
        f.write("    cb(\"    </%s>\\n\", %d, app_key);\n" % (key, len("    </%s>\n" % (key))))
        f.write("    cb(\"</%s-PDU>\\n\", %d, app_key);\n" % (key, len("</%s-PDU>\n" % (key))))

    f.write("    _ASN_ENCODED_OK(er);\n")
    #if key not in ieofielist.values():
        #f.write("cb_failed:\n")
        #f.write("    return er;\n")
    f.write("}\n\n")


#Generate xer print functions
f = open(outdir + fileprefix + '_compare.c', 'w')
outputHeaderToFile(f, filename)
f.write("#include <stdlib.h>\n")
f.write("#include <stdio.h>\n\n")
f.write("#include <asn_application.h>\n#include <asn_internal.h>\n\n")
f.write("#include \"%s_common.h\"\n#include \"%s_ies_defs.h\"\n" % (fileprefix, fileprefix))
f.write("#include \"%s-ProtocolIE-ID.h\"\n\n" % (fileprefix_first_upper))


for key in iesDefs:
    if key in ieofielist.values():
        continue
    structName = re.sub('ies', '', key)
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', key))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    if asn1cStruct.rfind('_') == len(asn1cStruct) - 1:
        asn1cStruct = asn1cStruct[:-1]
    asn1cStructfirstlower = asn1cStruct[:1].lower() + asn1cStruct[1:]
    firstwordlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    iesaccess = ""
    if key not in ieofielist.values():
        iesaccess = "%s_ies." % (firstwordlower)

    keyName = re.sub('-', '_', key)
    keyupperunderscore = keyName.upper()
    # No IE to encode...
    if len(iesDefs[key]["ies"]) == 0:
        continue

    f.write("asn_comp_rval_t * %s_compare_%s(\n" % (fileprefix, re.sub('-', '_', structName.lower())))
    f.write("    %s_t *%s1,\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))
    f.write("    %s_t *%s2) {\n\n" % (re.sub('-', '_', key), lowerFirstCamelWord(re.sub('-', '_', key))))

    f.write("    asn_comp_rval_t *rv = NULL;\n\n")
    f.write("    asn_comp_rval_t *rv2 = NULL;\n\n")

    f.write("    assert(%s1 != NULL);\n" % (lowerFirstCamelWord(re.sub('-', '_', key))));
    f.write("    assert(%s2 != NULL);\n" % (lowerFirstCamelWord(re.sub('-', '_', key))));

    loop = 0
    for ie in iesDefs[key]["ies"]:
        iename = re.sub('-', '_', re.sub('id-', '', ie[0]))
        ienameunderscore = re.sub('-', '_', iename)
        ienamefirstwordlower = lowerFirstCamelWord(iename)
        ieupperunderscore = re.sub('-', '_', re.sub('id-', '', ie[0])).upper()
        ietypeunderscore = re.sub('-', '_', ie[2])

        if ie[3] != "mandatory":

            loop = loop + 1
            if loop == 1:
                #f.write("    %s_IE_t *ie1 = NULL;\n" % (fileprefix_first_upper))
                #f.write("    %s_IE_t *ie2 = NULL;\n" % (fileprefix_first_upper))
                f.write("    if (%s1->presenceMask != %s2->presenceMask) {rv=calloc(1,sizeof(asn_comp_rval_t));rv->name = asn_DEF_%s.name;rv->structure1 = %s1;rv->structure2 = %s2;rv->err_code = COMPARE_ERR_CODE_VALUE_NULL; return rv;}\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), lowerFirstCamelWord(re.sub('-', '_', key)), ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', key)), lowerFirstCamelWord(re.sub('-', '_', key))))

            if ie[3] == "optional":
                f.write("    /* Optional field */\n")
            elif ie[3] == "conditional":
                f.write("    /* Conditional field */\n")
            f.write("    if (%s1->presenceMask & %s_%s_PRESENT) {\n" % (lowerFirstCamelWord(re.sub('-', '_', key)), keyupperunderscore, ieupperunderscore))


            if ie[2] in ieofielist.keys():
                f.write("        /* collection field */\n")
                f.write("        rv2 = %s_compare_%s(&%s1->%s, &%s2->%s);\n" % (fileprefix, ietypeunderscore.lower(), lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower ))
                f.write("        if(rv2) {")
                f.write("          if (NULL == rv) {")
                f.write("            rv = rv2;")
                f.write("          } else {")
                f.write("            rv2->next = rv;")
                f.write("            rv = rv2;")
                f.write("          }")
                f.write("          rv2 = NULL;")
                f.write("        }")
            else:
                f.write("        /* simple field */\n")
                f.write("        rv2 = asn_DEF_%s.compare(&asn_DEF_%s, &%s1->%s, &asn_DEF_%s, &%s2->%s); \n" % (ietypeunderscore, ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower, ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower ))
                f.write("        if (rv2) {")
                f.write("          if (NULL == rv) {")
                f.write("            rv = rv2;")
                f.write("          } else {")
                f.write("            rv2->next = rv;")
                f.write("            rv = rv2;")
                f.write("          }")
                f.write("          rv2 = NULL;")
                f.write("          if (!rv->name) rv->name = asn_DEF_%s.name;" % (ietypeunderscore))
                f.write("        }")

            f.write("        assert(0);\n");
            f.write("    }\n\n")

        else:
            if ie[2] in ieofielist.keys():
                f.write("    /* Mandatory collection field */\n")
                f.write("    rv2 = %s_compare_%s(&%s1->%s, &%s2->%s);\n" % (fileprefix, ietypeunderscore.lower(), lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower ))
                f.write("    if (rv2) {\n")
                f.write("      if (NULL == rv) {\n")
                f.write("        rv = rv2;\n")
                f.write("      } else {\n")
                f.write("        rv2->next = rv;\n")
                f.write("        rv = rv2;\n")
                f.write("      }\n")
                f.write("      rv2 = NULL;\n")
                f.write("    }\n")

            else:
                f.write("    /* Mandatory simple field */\n")
                f.write("    rv2 = asn_DEF_%s.compare(&asn_DEF_%s, &%s1->%s, &asn_DEF_%s, &%s2->%s);\n" % (ietypeunderscore, ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower, ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', key)), ienamefirstwordlower ))
                f.write("    if(rv2) {\n")
                f.write("      if (NULL == rv) {\n")
                f.write("        rv = rv2;\n")
                f.write("      } else {\n")
                f.write("        rv2->next = rv;\n")
                f.write("        rv = rv2;\n")
                f.write("      }\n")
                f.write("      rv2 = NULL;\n")
                f.write("      if (!rv->name) rv->name = asn_DEF_%s.name;\n" % (ietypeunderscore))
                f.write("    }\n")
    f.write("    return rv;\n")
    f.write("}\n\n")

for (key, value) in iesDefs.items():
    if key not in ieofielist.values():
        continue

    ie = value["ies"][0]
    ietypeunderscore = re.sub('-', '_', ie[2])
    asn1cStruct = re.sub('-', '_', re.sub('IEs', '', re.sub('-IEs', '', key)))
    asn1cStruct = re.sub('Item', 'List', asn1cStruct)
    firstwordlower = re.sub('Item', 'List', re.sub('enb', 'eNB', lowerFirstCamelWord(asn1cStruct)))

    for (i, j) in ieofielist.items():
        if j == key:
            break

    f.write("extern asn_TYPE_descriptor_t asn_DEF_%s;\n" % (ietypeunderscore))

    f.write("asn_comp_rval_t * %s_compare_%s(\n" % (fileprefix, re.sub('-', '_', i).lower()))
    f.write("    %sIEs_t *%sIEs1,\n" % (re.sub('-', '_', i), lowerFirstCamelWord(re.sub('-', '_', i))))
    f.write("    %sIEs_t *%sIEs2) {\n\n" % (re.sub('-', '_', i), lowerFirstCamelWord(re.sub('-', '_', i))))
    f.write("    int i;\n")
    f.write("    asn_comp_rval_t *rv = NULL;\n\n")
    f.write("    asn_comp_rval_t *rv2 = NULL;\n\n")


    f.write("    assert(%sIEs1 != NULL);\n" % (lowerFirstCamelWord(re.sub('-', '_', i))));
    f.write("    assert(%sIEs2 != NULL);\n\n" % (lowerFirstCamelWord(re.sub('-', '_', i))));

    f.write("    for (i = 0; i < %sIEs1->%s.count; i++) {\n" % (lowerFirstCamelWord(re.sub('-', '_', i)), re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
    f.write("        rv2 = asn_DEF_%s.compare(&asn_DEF_%s, %sIEs1->%s.array[i], &asn_DEF_%s, %sIEs2->%s.array[i]);\n" % (ietypeunderscore, ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', i)), re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key))), ietypeunderscore, lowerFirstCamelWord(re.sub('-', '_', i)), re.sub('IEs', '', lowerFirstCamelWord(re.sub('-', '_', key)))))
    f.write("        if(rv2) {")
    f.write("          if (NULL == rv) {")
    f.write("            rv = rv2;")
    f.write("          } else {")
    f.write("            rv2->next = rv;")
    f.write("            rv = rv2;")
    f.write("          }")
    f.write("          rv2 = NULL;")
    f.write("        }")
    f.write("    }\n")
    f.write("    return rv;\n")
    f.write("}\n\n")

