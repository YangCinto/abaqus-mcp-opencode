"""Example 1: 7.62mm bullet penetrating 10mm steel plate at 850m/s"""
from abaqus import mdb
from abaqusConstants import *
from regionToolset import Region
import mesh

model = mdb.Model(name='BulletPlate')

# Steel plate
steel = model.Material(name='Steel')
steel.Density(table=((7850.0,),))
steel.Elastic(table=((210.0e9, 0.3),))
steel.Plastic(table=((400.0e6,0.0),(500.0e6,0.1),(600.0e6,0.2),(700.0e6,0.3),(800.0e6,0.5)))

# Bullet (very hard)
bm = model.Material(name='BulletMat')
bm.Density(table=((8000.0,),))
bm.Elastic(table=((210.0e9, 0.3),))
bm.Plastic(table=((2000.0e6,0.0),(2100.0e6,0.05)))

# Plate 200x200x10mm
s = model.ConstrainedSketch(name='S', sheetSize=0.5)
s.rectangle(point1=(-0.1,-0.1), point2=(0.1,0.1))
plate = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
plate.BaseSolidExtrude(sketch=s, depth=0.01)

# Bullet: cylinder r=3.81mm, h=30mm
s2 = model.ConstrainedSketch(name='S2', sheetSize=0.1)
s2.CircleByCenterPerimeter(center=(0.0,0.0), point1=(0.00381,0.0))
bullet = model.Part(name='Bullet', dimensionality=THREE_D, type=DEFORMABLE_BODY)
bullet.BaseSolidExtrude(sketch=s2, depth=0.03)

# Sections
model.HomogeneousSolidSection(name='SteelSection', material='Steel')
model.HomogeneousSolidSection(name='BulletSection', material='BulletMat')
plate.SectionAssignment(region=Region(cells=plate.cells), sectionName='SteelSection')
bullet.SectionAssignment(region=Region(cells=bullet.cells), sectionName='BulletSection')

# Assembly
a = model.rootAssembly
pi = a.Instance(name='Plate-1', part=plate, dependent=ON)
bi = a.Instance(name='Bullet-1', part=bullet, dependent=ON)
a.translate(('Plate-1',), (0.0,0.0,-0.005))
a.translate(('Bullet-1',), (0.0,0.0,0.02))

# Step
model.ExplicitDynamicsStep(name='Penetration', previous='Initial',
    timePeriod=2.0e-4, nlgeom=ON)
model.fieldOutputRequests['F-Output-1'].setValues(
    numIntervals=50, variables=('S','E','U','V','STATUS','MISESMAX'))

# Contact
model.ContactExp(name='Contact', createStepName='Initial')
cp = model.ContactProperty('IntProp')
cp.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON)

# Fix back face of plate
bf = pi.faces.findAt(((0.0, 0.0, -0.005),))
fix_set = a.Set(name='PlateFixSet', faces=bf)
model.EncastreBC(name='PlateFix', createStepName='Initial', region=fix_set)

# Bullet velocity along -Z
model.Velocity(name='BulletVel', region=Region(cells=bi.cells),
    field='', velocity1=0.0, velocity2=0.0, velocity3=-850.0)

# Mesh
e1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=EXPLICIT)
plate.setElementType(regions=(plate.cells,), elemTypes=(e1,))
plate.seedPart(size=0.002)
plate.generateMesh()
bullet.seedPart(size=0.002)
bullet.generateMesh()

# Job
mdb.Job(name='bullet_plate_impact', model='BulletPlate',
    description='7.62mm vs 10mm plate', type=ANALYSIS, numCpus=1)
print('OK: bullet_plate_impact')
