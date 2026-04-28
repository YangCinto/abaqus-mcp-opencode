from abaqus import *
from abaqusConstants import *
from caeModules import *
import mesh
import regionToolset


MODEL_NAME = 'BulletPlatePenetration'
JOB_NAME = 'bullet_plate_penetration'

# Consistent SI unit set: m, kg, s, Pa.
PLATE_SIZE = 0.20
PLATE_THICKNESS = 0.010
BULLET_RADIUS = 0.005
BULLET_TIP_RADIUS = 0.001
BULLET_CYL_LENGTH = 0.022
BULLET_NOSE_LENGTH = 0.008
BULLET_GAP = 0.002
BULLET_SPEED = 800.0


def delete_existing():
    if MODEL_NAME in mdb.models:
        del mdb.models[MODEL_NAME]
    if JOB_NAME in mdb.jobs:
        del mdb.jobs[JOB_NAME]


def build_materials(model):
    steel = model.Material(name='Mild steel plate')
    steel.Density(table=((7850.0,),))
    steel.Elastic(table=((210.0e9, 0.30),))
    steel.Plastic(table=((400.0e6, 0.0), (650.0e6, 0.08), (800.0e6, 0.20)))

    bullet = model.Material(name='Hardened steel bullet')
    bullet.Density(table=((7850.0,),))
    bullet.Elastic(table=((210.0e9, 0.30),))
    bullet.Plastic(table=((1200.0e6, 0.0), (1600.0e6, 0.15)))

    model.HomogeneousSolidSection(name='Plate section', material='Mild steel plate')
    model.HomogeneousSolidSection(name='Bullet section', material='Hardened steel bullet')


def build_plate(model):
    sketch = model.ConstrainedSketch(name='plate_profile', sheetSize=0.4)
    half = PLATE_SIZE / 2.0
    sketch.rectangle(point1=(-half, -half), point2=(half, half))
    part = model.Part(name='Steel plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseSolidExtrude(sketch=sketch, depth=PLATE_THICKNESS)
    del model.sketches['plate_profile']

    region = regionToolset.Region(cells=part.cells)
    part.SectionAssignment(region=region, sectionName='Plate section')

    part.seedPart(size=0.005, deviationFactor=0.1, minSizeFactor=0.1)
    elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=EXPLICIT)
    part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
    part.generateMesh()
    return part


def build_bullet(model):
    total_length = BULLET_NOSE_LENGTH + BULLET_CYL_LENGTH
    sketch = model.ConstrainedSketch(name='bullet_profile', sheetSize=0.08)
    sketch.ConstructionLine(point1=(0.0, -0.01), point2=(0.0, total_length + 0.01))
    # A tiny flat tip avoids degenerate near-zero-volume elements at a sharp point.
    sketch.Line(point1=(0.0, 0.0), point2=(BULLET_TIP_RADIUS, 0.0))
    sketch.Line(point1=(BULLET_TIP_RADIUS, 0.0),
                point2=(BULLET_RADIUS, BULLET_NOSE_LENGTH))
    sketch.Line(point1=(BULLET_RADIUS, BULLET_NOSE_LENGTH),
                point2=(BULLET_RADIUS, total_length))
    sketch.Line(point1=(BULLET_RADIUS, total_length), point2=(0.0, total_length))
    sketch.Line(point1=(0.0, total_length), point2=(0.0, 0.0))

    part = model.Part(name='Bullet', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseSolidRevolve(sketch=sketch, angle=360.0, flipRevolveDirection=OFF)
    del model.sketches['bullet_profile']

    region = regionToolset.Region(cells=part.cells)
    part.SectionAssignment(region=region, sectionName='Bullet section')

    part.seedPart(size=0.0025, deviationFactor=0.1, minSizeFactor=0.1)
    elem_type = mesh.ElemType(elemCode=C3D4, elemLibrary=EXPLICIT)
    part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
    part.generateMesh()
    return part


def build_assembly_and_loads(model, plate, bullet):
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)

    plate_inst = assembly.Instance(name='Steel plate-1', part=plate, dependent=ON)
    bullet_inst = assembly.Instance(name='Bullet-1', part=bullet, dependent=ON)

    # Revolved bullet axis is local Y; rotate to align the shot direction with global Z.
    assembly.rotate(instanceList=('Bullet-1',), axisPoint=(0.0, 0.0, 0.0),
                    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
    assembly.translate(instanceList=('Bullet-1',),
                       vector=(0.0, 0.0, PLATE_THICKNESS + BULLET_GAP))

    model.ExplicitDynamicsStep(name='Impact', previous='Initial', timePeriod=8.0e-5,
                               improvedDtMethod=ON)

    contact = model.ContactProperty('Frictional hard contact')
    contact.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON,
                           constraintEnforcementMethod=DEFAULT)
    contact.TangentialBehavior(formulation=PENALTY, directionality=ISOTROPIC,
                               slipRateDependency=OFF, pressureDependency=OFF,
                               temperatureDependency=OFF, dependencies=0,
                               table=((0.12,),), shearStressLimit=None,
                               maximumElasticSlip=FRACTION,
                               fraction=0.005, elasticSlipStiffness=None)
    interaction = model.ContactExp(name='General contact', createStepName='Impact')
    interaction.includedPairs.setValuesInStep(stepName='Impact', useAllstar=ON)
    interaction.contactPropertyAssignments.appendInStep(
        stepName='Impact', assignments=((GLOBAL, SELF, 'Frictional hard contact'),)
    )

    half = PLATE_SIZE / 2.0
    tol = 1.0e-6
    edge_faces = plate_inst.faces.getByBoundingBox(xMin=-half - tol, xMax=-half + tol)
    edge_faces += plate_inst.faces.getByBoundingBox(xMin=half - tol, xMax=half + tol)
    edge_faces += plate_inst.faces.getByBoundingBox(yMin=-half - tol, yMax=-half + tol)
    edge_faces += plate_inst.faces.getByBoundingBox(yMin=half - tol, yMax=half + tol)
    model.EncastreBC(name='Clamped plate edges', createStepName='Initial',
                    region=regionToolset.Region(faces=edge_faces))

    model.Velocity(name='Bullet initial velocity', region=regionToolset.Region(cells=bullet_inst.cells),
                   field='', distributionType=MAGNITUDE, velocity1=0.0,
                   velocity2=0.0, velocity3=-BULLET_SPEED, omega=0.0)

    model.FieldOutputRequest(name='Impact fields', createStepName='Impact',
                             variables=('S', 'PEEQ', 'U', 'V', 'A', 'STATUS'))
    model.HistoryOutputRequest(name='Bullet energy', createStepName='Impact',
                               variables=('ALLIE', 'ALLKE', 'ALLWK', 'ETOTAL'))


def create_job():
    mdb.Job(name=JOB_NAME, model=MODEL_NAME, type=ANALYSIS,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE,
            description='Abaqus/Explicit demo: rigid-like bullet penetration of a steel plate.',
            parallelizationMethodExplicit=DOMAIN, multiprocessingMode=DEFAULT,
            numDomains=4, numCpus=4)
    mdb.jobs[JOB_NAME].writeInput(consistencyChecking=OFF)
    mdb.saveAs(pathName=JOB_NAME + '.cae')


delete_existing()
model = mdb.Model(name=MODEL_NAME)
build_materials(model)
plate_part = build_plate(model)
bullet_part = build_bullet(model)
build_assembly_and_loads(model, plate_part, bullet_part)
create_job()

print('BULLET_PLATE_PROJECT_CREATED')
