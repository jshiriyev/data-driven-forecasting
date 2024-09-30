from dataclasses import dataclass

@dataclass(frozen=True)
class WellStatus:

  prospect      : "white"

  construction  : "gray"
  drilling      : "purple"
  completion    : "yellow"
  installation  : "pink"

  delay         : "white"
  mobilization  : "black"
  
  optimization  : "lightgreen"
  remediation   : "lightgreen"
  recompletion  : "lighgreen"
  fishing       : "red"
  sidetrack     : "darkblue"

  production    : "darkgreen"
  injection     : "blue"
