f = open('/app/pages/1_Overview.py')
c = f.read()
f.close()

c = c.replace(
    '    models = list(comparison.keys())',
    '    models = [m for m in comparison if isinstance(comparison[m], dict)]'
)

f = open('/app/pages/1_Overview.py', 'w')
f.write(c)
f.close()
print('DONE - 1_Overview fixed')
