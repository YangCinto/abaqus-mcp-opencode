from odbAccess import openOdb
from abaqusConstants import MISES


ODB_PATH = 'bullet_plate_penetration.odb'


def max_scalar(field):
    if not field.values:
        return None
    return max(v.data for v in field.values)


def bullet_z_displacement(frame):
    if 'U' not in frame.fieldOutputs:
        return None
    values = [
        v.data[2] for v in frame.fieldOutputs['U'].values
        if v.instance and v.instance.name == 'BULLET-1'
    ]
    if not values:
        return None
    return sum(values) / float(len(values))


odb = openOdb(ODB_PATH, readOnly=True)
try:
    step = odb.steps['Impact']
    final = step.frames[-1]
    print('ODB:', ODB_PATH)
    print('Step:', step.name)
    print('Frames:', len(step.frames))
    print('Final step time:', final.frameValue)

    if 'PEEQ' in final.fieldOutputs:
        print('Max PEEQ:', max_scalar(final.fieldOutputs['PEEQ']))
    if 'S' in final.fieldOutputs:
        mises_values = final.fieldOutputs['S'].getScalarField(invariant=MISES)
        print('Max Mises stress:', max_scalar(mises_values))

    dz = bullet_z_displacement(final)
    if dz is not None:
        print('Average bullet U3:', dz)
finally:
    odb.close()
