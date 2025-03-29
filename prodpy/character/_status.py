from dataclasses import dataclass, fields

@dataclass(frozen=True)
class Status:

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

  @staticmethod
  def fields() -> list:
    return [field.name for field in fields(Status)]