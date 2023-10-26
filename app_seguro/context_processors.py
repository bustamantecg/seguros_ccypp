def user_groups_processor(request):
    groups = []
    user = request.user
    if user.is_authenticated:
        groups = list(user.groups.values_list('name', flat=True))
    return {'groups': groups}


def grupos_de_usuario(request):
    pertenece_a_empleados = request.user.groups.filter(name='Empleados').exists()
    pertenece_a_aseguradores = request.user.groups.filter(name='Aseguradores').exists()
    pertenece_a_administradores = request.user.groups.filter(name='Administradores').exists()
    pertenece_a_asegurados = request.user.groups.filter(name='Asegurados').exists()

    return {
        'pertenece_a_empleados': pertenece_a_empleados,
        'pertenece_a_aseguradores': pertenece_a_aseguradores,
        'pertenece_a_administradores': pertenece_a_administradores,
        'pertenece_a_asegurados':pertenece_a_asegurados,
    }