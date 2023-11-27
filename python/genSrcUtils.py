import string
import importUtils

#================================================================================
class genSrcUtils(importUtils.importUtils):
#--------------------------------------------------------------------------------
  def __init__(self):
    importUtils.importUtils.__init__(self)
    self.namespace = 'unknown::'
    self.generatedTypedefs = []
    self.generatedEnums = []
    self.generatedTypes = []
#--------------------------------------------------------------------------------
  def reset(self,godClass):
    importUtils.importUtils.reset(self,godClass)
    self.generatedTypedefs = []
    self.generatedEnums = []
    self.generatedTypes = []
#--------------------------------------------------------------------------------
  def genDesc(self, godClass):
    s = ''
    classAtt = godClass['attrs']
    if 'desc' in classAtt:                                                 # add class attribute desc
      s += classAtt['desc']
    if 'desc' in godClass:                                                # add elements desc
      for desc in godClass['desc']:
        s += desc['cont']
    if len(s):
      s = s.replace('\n','')
      s = ' '.join(s.split())
      s2 = ''                                                                    # text reformatting (<80chars)
      while len(s):
        if len(s) < 77:
          if len(s2) : s2 += '\n * ' + s
          else : s2 += s
          s = ''
        else:
          pos = s.rfind(' ',0,77)
          if len(s2) : s2 += '\n * ' + s[:pos]
          else : s2 += s[:pos]
          s = s[pos+1:]
      s = s2
    return s
#--------------------------------------------------------------------------------
  def genTypedefs(self,modifier,godClass):
    s = ''
    if 'typedef' in godClass:
      for td in godClass['typedef']:
        tdAtt = td['attrs']
        if tdAtt['access'] == modifier.upper() or modifier == 'all':
          s += '  /// %s\n' % tdAtt['desc']
          s += '  typedef %s %s;\n' % (tdAtt['type'], tdAtt['def'])
          self.generatedTypedefs.append(tdAtt['def'])
          self.generatedTypes.append(tdAtt['def'])
    return s
#--------------------------------------------------------------------------------
  def genEnums(self,modifier,godClass):
    s = ''
    if 'enum' in godClass:
      for enum in godClass['enum']:
        enumAtt = enum['attrs']
        if enumAtt['access'] == modifier.upper() or modifier == 'all':
          self.generatedEnums.append(enumAtt['name'])
          self.generatedTypes.append(enumAtt['name'])
          indent = ' ' * (len(enumAtt['name'])+8)
          s += '  /// %s\n' % enumAtt['desc']
          maxlenval = 0
          valatt = 0
          s += '  enum %s{' % ( enumAtt['name'] )
          if 'value' in enumAtt:
            values = enumAtt['value'].split(',')
            if len(values):
              s += ' %s' % values[0].strip()
              maxlenval = len(values[0])
              valatt = 1
              if (len(values)>1):
                for value in values[1:] :
                  s += ',\n%s %s' % ( indent, value.strip() )
                  maxlenval = max(maxlenval,len(value.strip()))
          evall = []
          if 'enumval' in enum:
            if valatt : s += ',\n'+indent
            for eval in enum['enumval']:
              evalAtt = eval['attrs']
              if 'value' in evalAtt : evall.append([evalAtt['name']+ ' = ' + evalAtt['value'], evalAtt['desc']])
              else                        : evall.append([evalAtt['name'], evalAtt['desc']])
              maxlenval = max(maxlenval,len(evall[-1][0]))
            maxlenval += 1
            s += ' %s // %s' % ((evall[0][0]+',').ljust(maxlenval),evall[0][1])
            for e in evall[1:-1]:
              s += '\n%s %s // %s' % (indent, (e[0]+',').ljust(maxlenval),e[1])
            s += '\n%s %s // %s' % (indent, evall[-1][0].ljust(maxlenval), evall[-1][1])
          s += '\n    };\n'
    return s
#--------------------------------------------------------------------------------
  def genEnumOstreamOverloads(self, godClass, className=''):
    s = ''
    if 'enum' in godClass:
      self.addInclude('ostream',1)
      for enum in godClass['enum']:
        enumAtt = enum['attrs']
        if enumAtt['access'] == 'PUBLIC':
          enumType = className+'::'+enumAtt['name']
          s += 'inline std::ostream & operator << (std::ostream & s, %s e) {\n' % (enumType)
          s += '  switch (e) {\n'
          maxLen = 0
          values = []
          if 'value' in enumAtt:
            for v in enumAtt['value'].split(',') :
              name = v.split('=')[0].strip()
              maxLen = max(len(name),maxLen)
              values.append(name)
          if 'enumval' in enum:
            for eval in enum['enumval'] : 
              name = eval['attrs']['name']
              maxLen = max(maxLen, len(name))
              values.append(name)
          for v in values :
            s += '    case %s::%s : return s << "%s";\n' % ( className, v.ljust(maxLen), v )
          s += '    default : return s << "ERROR wrong value for enum %s";\n' % enumType
          s += '  }\n'
          s += '}\n\n'
    return s
#--------------------------------------------------------------------------------
  def genEnumConversions(self, godClass, className=''):
    defs  = ''
    maps  = ''
    dcls = ''
    if 'enum' in godClass:
      for enum in godClass['enum'] :
        enumAtt = enum['attrs']
        if enumAtt['strTypConv'] == 'TRUE':
          self.addInclude('GaudiKernel/VectorMap')
          enumType = enumAtt['name']
          enumUnknown = enumAtt['unknownValue']

          maxLen = 0
          values = []
          if 'value' in enumAtt:
            for v in enumAtt['value'].split(',') :
              name = v.split('=')[0].strip()
              maxLen = max(len(name),maxLen)
              values.append(name)
          if 'enumval' in enum:
            for eval in enum['enumval'] : 
              name = eval['attrs']['name']
              maxLen = max(maxLen, len(name))
              values.append(name)

          dcls += '  /// conversion of string to enum for type %s\n' % enumType
          dcls += '  static %s::%s %sToType (const std::string & aName);\n\n' % ( className, enumType, enumType )
          dcls += '  /// conversion to string for enum type %s\n' % enumType
          dcls += '  static std::string %sToString(int aEnum);\n' % enumType

          maps += '  static GaudiUtils::VectorMap<std::string,%s> & s_%sTypMap();\n' % (enumType, enumType)

          defs += 'inline GaudiUtils::VectorMap<std::string,%s::%s> & %s::s_%sTypMap() {\n' % ( className, enumType, className, enumType )
          defs += '  static GaudiUtils::VectorMap<std::string,%s> m;\n' % enumType
          defs += '  if (m.empty()) {\n'
          for v in values : defs += '    m.insert("%s",%s);\n' % (v, v)
          defs += '  };\n'
          defs += '  return m;\n'
          defs += '}\n\n'
          defs += 'inline %s::%s %s::%sToType(const std::string & aName) {\n' % (className, enumType, className, enumType)
          defs += '  GaudiUtils::VectorMap<std::string,%s>::iterator iter =  s_%sTypMap().find(aName);\n' % ( enumType, enumType )
          defs += '  return ( iter != s_%sTypMap().end() ? iter->second : %s );\n' % (enumType, enumUnknown)
          defs += '}\n\n'
          defs += 'inline std::string %s::%sToString(int aEnum) {\n' % (className, enumType)
          defs += '  GaudiUtils::VectorMap<std::string,%s>::iterator iter = s_%sTypMap().begin();\n' % (enumType, enumType)
          defs += '  while ( iter != s_%sTypMap().end() && iter->second != aEnum ) ++iter;\n' % enumType
          defs += '  return ( iter != s_%sTypMap().end() ? iter->first : "%s");\n' % (enumType, enumUnknown)
          defs += '}\n'

    return defs,maps,dcls
#--------------------------------------------------------------------------------
  def genAttributes(self,modifier,godClass,namespace=0):
    s = ''
    maxLenTypNam = [0,0,0]
    if 'attribute' in godClass:
      for att in godClass['attribute'] :
        if (att['attrs']['access'] == modifier.upper() or modifier == 'all') and att['attrs']['storage'] == 'TRUE' :
          maxLenTypNam[0] = max(maxLenTypNam[0], len(att['attrs']['type']))
          maxLenTypNam[1] = max(maxLenTypNam[1], len(att['attrs']['name']))
          if namespace and 'init' in att['attrs']:
            maxLenTypNam[2] = max(maxLenTypNam[1], len(att['attrs']['init']))
    if 'relation' in godClass:
      for rel in godClass['relation'] :
        if rel['attrs']['access'] == modifier.upper() or modifier == 'all':
          typlen = len(rel['attrs']['type'])
          if rel['attrs']['multiplicity'] != '1' : 
            maxLenTypNam[0] = max(maxLenTypNam[0], 9)
          else                                   : 
            maxLenTypNam[0] = max(maxLenTypNam[0], 4)
          maxLenTypNam[1] = max(maxLenTypNam[1], len(rel['attrs']['name']))
    if 'SmartRelation' in godClass:
      for rel in godClass['SmartRelation'] :
        if rel['attrs']['access'] == modifier.upper() or modifier == 'all':
          maxLenTypNam[0] = max(maxLenTypNam[0], 12)
          maxLenTypNam[1] = max(maxLenTypNam[1], len(rel['attrs']['name']))
    if namespace :
      maxLenTypNam[1] += 1
      if maxLenTypNam[2] : maxLenTypNam[2] += 4
    else : maxLenTypNam[1] += 3
    if 'attribute' in godClass:
      for att in godClass['attribute'] :
        attAtt = att['attrs']
        if (attAtt['access'] == modifier.upper() or modifier == 'all') and att['attrs']['storage'] == 'TRUE' :
          transient = ''
          length = ''
          pointer = ''
          if attAtt['transient'] == 'TRUE':
            transient = '!'
          elif attAtt['pointer'] == 'TRUE':
            pointer = '->'
          elif 'length' in attAtt:
            length = '[' + str( attAtt['length'] ) + ']'
          attType = attAtt['type']
          if attType in ['bitfield8','bitfield16','bitfield','bitfield32','bitfield64']:
            self.bitfieldEnums[modifier.lower()] += self.genBitfield(att)
            if   attType in ['bitfield8']             : attAtt['type'] = 'unsigned char'
            elif attType in ['bitfield16']            : attAtt['type'] = 'unsigned short int'
            elif attType in ['bitfield','bitfield32'] : attAtt['type'] = 'unsigned int'
            elif attType in ['bitfield64']            : attAtt['type'] = 'ulonglong'
          name = attAtt['name']
          namespaceInit = ''
          if namespace :
            if 'init' in attAtt : namespaceInit = ' = %s;'%attAtt['init']
          else :
            name = 'm_%s;' % name
          s += '  %s %s%s //%s%s%s %s\n' % (attAtt['type'].ljust(maxLenTypNam[0]), \
                                        name.ljust(maxLenTypNam[1]), \
                                        namespaceInit.ljust(maxLenTypNam[2]), \
                                        transient, \
                                        length, \
                                        pointer, \
                                        attAtt['desc'])
    if 'relation' in godClass:
      for rel in godClass['relation'] :
        relAtt = rel['attrs']
        if relAtt['access'] == modifier.upper() or modifier == 'all':
          if relAtt['multiplicity'] == '1' : 
            relType = 'TRef' 
            self.addInclude('TRef')
          else: 
            relType = 'TRefArray'
            self.addInclude('TRefArray')
          s += '  %s %s // %s\n' % (relType.ljust(maxLenTypNam[0]),
                                        ('m_%s;'%relAtt['name']).ljust(maxLenTypNam[1]), relAtt['desc'])
    if 'SmartRelation' in godClass:
      self.addInclude('EDMUtil/SmartRef')
      #if 'priority' in godClass['attrs'] and 'path' in godClass['attrs']:
      #  self.addInclude('DataRegistritionSvc/BookEDM.h')
      for rel in godClass['SmartRelation'] :
        relAtt = rel['attrs']
        if relAtt['access'] == modifier.upper() or modifier == 'all':
          relType = 'JM::SmartRef'
          s += '  %s %s // ||%s\n' % (relType.ljust(maxLenTypNam[0]),
                                        ('m_%s;'%relAtt['name']).ljust(maxLenTypNam[1]), relAtt['desc'])
    return s
#--------------------------------------------------------------------------------
  def genTemplateAttr(self,modifier,godClass,namespace=0):
    s = ''
    maxLenTypNam = [0,0,0]
    attList = []
    if 'template' in godClass:
      for att in godClass['template']:
        if (att['attrs']['access'] == modifier.upper() or modifier == 'all') and att['attrs']['storage'] == 'TRUE' :
          transient = ''
          length = ''
          pointer = ''
          if att['attrs']['transient'] == 'TRUE':
            transient = '!'
          elif att['attrs']['pointer'] == 'TRUE':
            pointer = '->'
          elif 'length' in att['attrs']:
            length = '[' + str( attAtt['length'] ) + ']'
          tempType = att['attrs']['type'] + '<'
          tempName = att['attrs']['name']
          maxLenTypNam[1] = max( maxLenTypNam[1], len(att['attrs']['name'] ) )
          if namespace and 'init' in att['attrs']:
            namespaceInit = ' = %s;' % att['attrs']['init']
            maxLenTypNam[2] = max( maxLenTypNam[2], len( att['attrs']['init'] ) )
          attTypeList = att['typename']
          depth = 0
          depthLength = { 0 : len( attTypeList ) }
          nameLength = len(att['attrs']['type'] ) + 2
          while True:
            if 'typename' in attTypeList[0]:
              tempType = tempType + attTypeList[0]['attrs']['type'] + '<'
              nameLength += len( attTypeList[0]['attrs']['type'] ) + 3 
              depthLength[depth] = depthLength[depth] - 1
              depth = depth + 1
              depthLength[depth] = len( attTypeList[0]['typename'] )
              attTypeList = attTypeList[0]['typename'] + attTypeList[1:]
            else:
              tempType = tempType + attTypeList[0]['attrs']['type'] + ','
              nameLength += len( attTypeList[0]['attrs']['type'] ) + 1
              depthLength[depth] = depthLength[depth] - 1
              attTypeList = attTypeList[1:]
            if depthLength[depth] == 0:
              if tempType.endswith( ',' ):
                tempType = tempType[:-1]
              tempType = tempType + '>,'
              depth = depth - 1
            if not attTypeList:
              if tempType.endswith( ',' ):
                tempType = tempType[:-1]
              while depth >= 0:
                tempType = tempType + '>'
                depth = depth - 1                
              break
          maxLenTypNam[0] = max( maxLenTypNam[0], nameLength - 1 )
          desc = att['attrs']['desc']
          namespaceInit = ''
          if namespace :
            if 'init' in att['attrs'] : namespaceInit = ' = %s;'%att['attrs']['init']
          else :
            tempName = 'm_%s;' % tempName
          attList.append( { 'tempType' : tempType, 'tempName' : tempName, 'namespaceInit' : namespaceInit, 'transient' : transient, 'length' : length, 'pointer' : pointer, 'desc' : desc } )
    if attList:
      for attDict in attList:    
        s += '  %s %s%s //%s%s%s %s\n' % (attDict['tempType'].ljust(maxLenTypNam[0]), \
                                      attDict['tempName'].ljust(maxLenTypNam[1]), \
                                      attDict['namespaceInit'].ljust(maxLenTypNam[2]), \
                                      attDict['transient'], \
                                      attDict['length'], \
                                      attDict['pointer'], \
                                      attDict['desc'])
    return s
#--------------------------------------------------------------------------------
  def genMethod(self,met,scopeName=''):
    s = ''
    indent = 0
    if (scopeName and 'code' not in met) : return s
    metAtt = met['attrs']
    if ( not scopeName ) :
      s += '  /// %s\n  ' % metAtt['desc']
      if 'template' in metAtt : s += 'template <%s>\n  ' % metAtt['template']
      indent += 2
      if metAtt['static'] == 'TRUE':
        s += 'static '
        indent += 7
      if metAtt['virtual'] in ['TRUE','PURE']:
        s += 'virtual '
        indent += 8
      if metAtt['friend'] == 'TRUE' :
        s += 'friend '
        indent += 7
    else :
      if 'template' in metAtt : s += 'template <%s>\n' % metAtt['template']      
      s += 'inline '
      scopeName += '::'
      indent += len(scopeName) + 7
    constF = ''
    if metAtt['const'] == 'TRUE' : constF = ' const'
    pList = []
    if 'argList' in metAtt: pList = self.tools.genParamsFromStrg(metAtt['argList'])
    if 'arg' in met       : pList = self.tools.genParamsFromElem(met['arg'])
    metRet = ''
    if metAtt['type'].strip() :  metRet = self.tools.genReturnFromStrg(metAtt['type'],self.generatedTypes,scopeName) + ' '
    if 'return' in met :   metRet = self.tools.genReturnFromElem(met['return'],self.generatedTypes,scopeName) + ' '
    if not scopeName and metRet[:len(self.namespace)] == self.namespace :
      metRet = metRet[len(self.namespace):]
    indent += len(metRet) + len(metAtt['name'])
    s += metRet + scopeName + metAtt['name'] + '('
    if len(pList):
      if scopeName : s += pList[0].split('=')[0]                                # in implementation strip off default arguments
      else         : s += pList[0]
      if len(pList[1:]):
        for p in pList[1:]:
          if scopeName : s += ',\n%s %s' % (indent*' ', p.split('=')[0])        # in implementation strip off default arguments
          else         : s += ',\n%s %s' % (indent*' ', p)

    s += ')' + constF
    if metAtt['virtual'] == 'PURE': s += ' = 0'
    if not scopeName : s += ';\n\n'
    else : 
      s += ' \n{\n%s\n}\n\n' % met['code'][0]['cont']
    return s
#--------------------------------------------------------------------------------
  def genMethods(self,modifier,godClass,clname=''):
    import os
    s = ''
    if 'method' in godClass:
      for met in godClass['method']:
        if met['attrs']['access'] == modifier.upper() or modifier == 'all':
          if 'scope' in godClass['attrs']:
             self.namespace=godClass['attrs']['scope']+'::'
          elif 'namespace' in godClass['attrs']:
             self.namespace=godClass['attrs']['namespace']+'::'
          elif 'GODSCOPE' in os.environ:
             self.namespace=os.environ['GODSCOPE']+'::'
          else:
             self.namespace='LHCb::'

          s += self.genMethod(met,clname)

    self.namespace='unknown::'
    return s[:-1]
#--------------------------------------------------------------------------------
  def comment(self,desc):
    "Util routine to allow multi line comments"
    return "\n".join(map(lambda l: "/// " + l, desc.split("\\n")))+"\n"

