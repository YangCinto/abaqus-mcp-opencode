"""Read ODB info for both simulations and save to JSON"""
from odbAccess import *
import json

def get_odb_summary(odb_path, name):
    """Extract summary from ODB file."""
    odb = openOdb(path=odb_path, readOnly=True)
    result = {
        'name': name,
        'parts': [],
        'steps': {},
        'frameCount': 0,
    }

    for part_name in odb.parts.keys():
        p = odb.parts[part_name]
        result['parts'].append({
            'name': part_name,
            'nodeCount': len(p.nodes),
            'elementCount': len(p.elements),
        })

    for step_name in odb.steps.keys():
        step = odb.steps[step_name]
        frames_info = []
        max_mises = 0.0
        for i, frame in enumerate(step.frames):
            frames_info.append({
                'frameId': i,
                'frameValue': frame.frameValue,
                'description': frame.description,
            })
            try:
                stress_field = frame.fieldOutputs['S']
                mises_values = [s.mises for s in stress_field.values if s.mises is not None]
                if mises_values:
                    max_mises = max(max_mises, max(mises_values))
            except Exception:
                pass

        result['steps'][step_name] = {
            'totalTime': step.totalTime if hasattr(step, 'totalTime') else None,
            'numFrames': len(step.frames),
            'maxMisesStress': max_mises,
            'frames': frames_info[:3],  # First 3 frames only
            'lastFrame': frames_info[-1] if frames_info else None,
        }
        result['frameCount'] += len(step.frames)

    odb.close()
    return result


base = r'C:\Users\Cinto\Desktop\Test2\abaqus-test03'
results = [
    get_odb_summary(f'{base}\\bullet_plate_impact.odb', 'Example 1: Bullet vs Plate'),
    get_odb_summary(f'{base}\\bullet_pipe_impact.odb', 'Example 2: Bullet vs Pipe'),
]

output_path = r'C:\Users\Cinto\Desktop\Test2\abaqus-test03\odb_summary.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f'Saved summary to {output_path}')
print(f'Plate max Mises: {results[0]["steps"]["Penetration"]["maxMisesStress"]:.2e} Pa')
print(f'Pipe max Mises: {results[1]["steps"]["Penetration"]["maxMisesStress"]:.2e} Pa')
