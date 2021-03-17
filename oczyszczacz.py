new_lines=[]

new_f = open("output_clean5.txt", "a")

with open('output.txt') as old_f:
    for line in old_f:
        if line=='\n':
            flag = True
            if len(new_lines) ==9:
                new_lines.append(line)
                l = new_lines[4].split()
                if l[0] == 'Err:':



                    flag = False
                for i in range(5,9):
                    l = new_lines[i].split()
                    try:
                        k = int(l[0])
                    except:
                        flag = False
                if flag:
                    for l in new_lines:
                        new_f.write(l)
            else:
                new_lines=[]

        else:
           new_lines.append(line)


new_f.close()