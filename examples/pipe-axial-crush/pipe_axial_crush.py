import os, sys

target_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(target_dir)

from abaqus import *
from abaqusConstants import *
from odbAccess import *
import mesh

length = 200.0
outer_radius = 25.0
inner_radius = 20.0
E = 210e3
nu = 0.3
yield_stress = 250.0
compression = -10.0

print('Creating model...')
myModel = mdb.Model(name='PipeAxialCrush')

s = myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
s.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s.FixedConstraint(entity=s.geometry.findAt((0.0, 0.0)))
s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(outer_radius, 0.0))
s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(inner_radius, 0.0))

p = myModel.Part(name='Pipe', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseSolidExtrude(sketch=s, depth=length)

print('Defining material...')
mat = myModel.Material(name='Steel')
mat.Elastic(table=((E, nu),))
mat.Plastic(table=((yield_stress, 0.0), (300.0, 0.02), (350.0, 0.10), (380.0, 0.20)))

sec = myModel.HomogeneousSolidSection(name='PipeSection', material='Steel')
region = p.Set(cells=p.cells, name='All')
p.SectionAssignment(region=region, sectionName='PipeSection')

print('Building assembly...')
a = myModel.rootAssembly
a.DatumCsysByDefault(CARTESIAN)
inst = a.Instance(name='PipeInstance', part=p, dependent=ON)

print('Creating step (nlgeom=ON)...')
myModel.StaticStep(name='AxialCrush', previous='Initial',
                   nlgeom=ON, initialInc=0.01, minInc=1e-8, maxInc=0.05, maxNumInc=1000)

print('Applying BCs...')
mid_r = (outer_radius + inner_radius) / 2.0
bot = inst.faces.findAt(((mid_r, 0.0, 0.0),))
a.Set(faces=bot, name='Bottom')
myModel.DisplacementBC(name='FixBottom', createStepName='Initial',
                       region=a.sets['Bottom'],
                       u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0)

top = inst.faces.findAt(((mid_r, 0.0, length),))
a.Set(faces=top, name='Top')
myModel.DisplacementBC(name='AxialLoad', createStepName='AxialCrush',
                       region=a.sets['Top'], u3=compression)

print('Meshing...')
p.seedPart(size=2.5, deviationFactor=0.1, minSizeFactor=0.1)
elem1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
elem2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
elem3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
p.setElementType(regions=(p.cells,), elemTypes=(elem1, elem2, elem3))
p.generateMesh()

print('Creating job...')
job_name = 'PipeAxialCrush'
myJob = mdb.Job(name=job_name, model='PipeAxialCrush',
                description='Pipe axial crush - 10mm compression')

print('Submitting job...')
myJob.submit()
print('Waiting for completion...')
myJob.waitForCompletion()
print('Job completed!')

print('Post-processing...')
odb_path = os.path.join(target_dir, job_name + '.odb')
if os.path.exists(odb_path):
    odb = openOdb(path=odb_path, readOnly=True)
    step = odb.steps['AxialCrush']
    last_frame = step.frames[-1]

    s_field = last_frame.fieldOutputs['S']
    max_mises = max(v.mises for v in s_field.values)

    u_field = last_frame.fieldOutputs['U']
    max_u3 = max(abs(v.data[2]) for v in u_field.values)

    total_rf3 = 0.0
    try:
        nset = odb.rootAssembly.instances['PIPEINSTANCE'].nodeSets['BOTTOM']
        rf = last_frame.fieldOutputs['RF'].getSubset(region=nset)
        total_rf3 = sum(v.data[2] for v in rf.values)
    except Exception:
        try:
            nset = odb.rootAssembly.nodeSets['BOTTOM']
            rf = last_frame.fieldOutputs['RF'].getSubset(region=nset)
            total_rf3 = sum(v.data[2] for v in rf.values)
        except Exception as e:
            print('Note: could not extract RF from set:', str(e))

    print()
    print('=' * 50)
    print('  RESULTS')
    print('=' * 50)
    print(f'  Total reaction force RF3:  {total_rf3:>10.1f} N')
    print(f'  Max displacement U3:       {max_u3:>10.3f} mm')
    print(f'  Max von Mises stress:      {max_mises:>10.1f} MPa')
    print(f'  Total frames:              {len(step.frames):>10}')
    print('=' * 50)

    odb.close()
else:
    print(f'ODB not found at {odb_path}')

print('All done!')
