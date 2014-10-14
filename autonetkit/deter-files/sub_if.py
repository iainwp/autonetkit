import sys, re
from addr import addr_to_name

def main():
  rv = addr_to_name()
  # rv is a dict addr->ifname
  inf_file = sys.argv[1]
  map={}
  with open(inf_file, "r") as f:
    lines = f.read().splitlines()
    for x in lines:
      [a, i] = x.split(" ")
      if a in rv:
          map[i] = rv[a]

  for x in sys.argv[2:]:
    try:
      print "Processing file", x
      with open(x, "r") as f:
        contents = f.read()
        for i in map:
          contents = contents.replace(i, map[i])
        f.close()
    
      with open(x, "w") as f:
        f.write(contents)
        f.close()
    except FileNotFoundError:
      skip

if __name__ == '__main__':
  main()
