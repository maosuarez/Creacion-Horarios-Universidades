# Código con manejo de errores y comentarios ampliados.
# NOTA: Se respeta toda la lógica original; únicamente se agregan comentarios detallados.

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional
from app.database import get_db
from app.models.comment import Comment
from app.models.profile import Profile
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

# ---------------------------------------------------------------------------
# Funciones auxiliares con comentarios extendidos
# ---------------------------------------------------------------------------

def get_comment_or_404(comment_id: int, db: Session) -> Comment:
    """
    Recupera un comentario por su ID.

    - Si la consulta falla por error de base de datos → se lanza 500.
    - Si no encuentra el comentario → se lanza 404.

    Esta función encapsula toda la lógica de búsqueda y manejo
    de errores, evitando repetición en los endpoints.
    """
    try:
        # Intentamos obtener el comentario desde la base de datos.
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
    except SQLAlchemyError:
        # Error interno generado por SQLAlchemy (conexión, sintaxis, corrupción, etc.)
        raise HTTPException(status_code=500, detail="Error interno al consultar el comentario")

    # Si no existe el comentario, devolvemos un error 404 explícito.
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comentario con id {comment_id} no encontrado"
        )
    return comment

def check_comment_owner(comment: Comment, current_user: Profile):
    """
    Verifica si el usuario autenticado es propietario del comentario.

    - Si no lo es → error 403
    - Esta verificación centraliza la validación de permisos.
    """
    if comment.profile_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este comentario"
        )

# ---------------------------------------------------------------------------
# Crear comentario
# ---------------------------------------------------------------------------

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo comentario asignando automáticamente el usuario autenticado.

    Flujo:
    1. Validación opcional del curso (placeholder)
    2. Construcción del objeto Comment
    3. Inserción en la base de datos con manejo de errores por tipo
    4. Respuesta enriquecida con datos del autor
    """

    # Si el cliente envía course_id, aquí debería validarse que dicho curso exista.
    if comment_data.course_id is not None:
        # Placeholder para una futura validación real del curso.
        pass

    try:
        # Creamos el objeto Comment listo para persistir.
        new_comment = Comment(
            content=comment_data.content,
            course_id=comment_data.course_id,
            profile_id=current_user.id  # El autor del comentario es el usuario actual.
        )

        # Agregamos el nuevo comentario a la sesión.
        db.add(new_comment)
        # Confirmamos los cambios en la base de datos.
        db.commit()
        # Refrescamos para obtener la instancia final desde la BD.
        db.refresh(new_comment)

    except IntegrityError:
        # Error típico por violación de restricciones (FK, únicos, longitud, etc.)
        db.rollback()
        raise HTTPException(status_code=400, detail="Datos inválidos al crear el comentario")

    except SQLAlchemyError:
        # Cualquier otro error interno de SQLAlchemy.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al crear el comentario")

    except Exception:
        # Captura final para cualquier error que no pertenezca al mundo SQL.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error inesperado al crear el comentario")

    # Construcción de la respuesta final.
    response = CommentResponse.model_validate(new_comment)
    response.author_name = current_user.name
    response.author_email = current_user.email
    return response

# ---------------------------------------------------------------------------
# Listar comentarios
# ---------------------------------------------------------------------------

@router.get("/", response_model=CommentListResponse)
def list_comments(
    course_id: Optional[int] = Query(None, description="Filtrar por curso"),
    profile_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """
    Listado de comentarios con paginación y filtros opcionales.

    Flujo:
    1. Construcción de query base uniendo perfil
    2. Aplicación de filtros dinámicos
    3. Paginación controlada: offset + limit
    4. Manejo de errores ante fallos en consultas
    5. Respuesta con datos del autor incluido
    """
    try:
        # Se construye la consulta base con JOIN para obtener datos del perfil.
        query = db.query(Comment).join(Profile)

        # Si el cliente envió course_id, filtramos.
        if course_id is not None:
            query = query.filter(Comment.course_id == course_id)

        # Si el cliente envió profile_id, filtramos.
        if profile_id is not None:
            query = query.filter(Comment.profile_id == profile_id)

        # Contamos el total de coincidencias antes de paginar.
        total = query.count()

        # Calculamos el desplazamiento en función de la página actual.
        offset = (page - 1) * page_size

        # Ejecutamos la consulta final con paginación.
        comments = (
            query.order_by(Comment.created_at.desc())
                 .offset(offset)
                 .limit(page_size)
                 .all()
        )

    except SQLAlchemyError:
        # Error interno relacionado con la base de datos.
        raise HTTPException(status_code=500, detail="Error interno al listar comentarios")

    except Exception:
        # Cualquier otro error inesperado.
        raise HTTPException(status_code=500, detail="Error inesperado al listar comentarios")

    # Construcción manual de la lista de respuesta, agregando datos del autor.
    comments_response = []
    for comment in comments:
        comment_data = CommentResponse.model_validate(comment)
        comment_data.author_name = comment.profile.name
        comment_data.author_email = comment.profile.email
        comments_response.append(comment_data)

    return CommentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        comments=comments_response
    )

# ---------------------------------------------------------------------------
# Obtener comentario por ID
# ---------------------------------------------------------------------------

@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un comentario por ID a través de la función centralizada
    que maneja errores y validaciones.
    """
    try:
        comment = get_comment_or_404(comment_id, db)
        return CommentResponse.model_validate(comment)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(500, "Error al obtener el comentario")

# ---------------------------------------------------------------------------
# Obtener todos mis comentarios
# ---------------------------------------------------------------------------

@router.get("/me/all", response_model=CommentListResponse)
def get_my_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los comentarios asociados al usuario autenticado.

    - Se filtra directamente por el ID del usuario.
    - Se aplican mecanismos de paginación igual que en el listado general.
    - Manejo de errores robusto ante fallos SQL o inesperados.
    """
    try:
        # Filtramos únicamente los comentarios cuyo profile_id coincide.
        query = db.query(Comment).filter(Comment.profile_id == current_user.id)

        # Total sin paginación.
        total = query.count()

        # Paginación.
        offset = (page - 1) * page_size
        comments = (
            query.order_by(Comment.created_at.desc())
                 .offset(offset)
                 .limit(page_size)
                 .all()
        )

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al obtener tus comentarios")

    except Exception:
        raise HTTPException(status_code=500, detail="Error inesperado al obtener tus comentarios")

    # Se incluye el nombre y correo del autor (siempre el usuario autenticado).
    comments_response = []
    for comment in comments:
        comment_data = CommentResponse.model_validate(comment)
        comment_data.author_name = current_user.name
        comment_data.author_email = current_user.email
        comments_response.append(comment_data)

    return CommentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        comments=comments_response
    )

# ---------------------------------------------------------------------------
# Actualizar comentario
# ---------------------------------------------------------------------------

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el contenido de un comentario existente.

    Flujo:
    1. Obtener el comentario y validar existencia
    2. Verificar propiedad del comentario
    3. Actualizar contenido
    4. Manejo exhaustivo de errores SQL y lógicos
    5. Respuesta enriquecida
    """

    try:
        # Obtención del comentario (si falla lanza 404).
        comment = get_comment_or_404(comment_id, db)

        # Validación de permisos (si no es dueño → 403).
        check_comment_owner(comment, current_user)

        # Actualizamos solo el campo permitido.
        comment.content = comment_data.content

        # Persistimos los cambios.
        db.commit()
        db.refresh(comment)

    except HTTPException:
        # Errores 404/403 se reenvían.
        raise

    except IntegrityError:
        # Problemas con integridad (longitud, valores inválidos, etc.)
        db.rollback()
        raise HTTPException(status_code=400, detail="Datos inválidos al actualizar el comentario")

    except SQLAlchemyError:
        # Errores internos de SQLAlchemy.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al actualizar el comentario")

    except Exception:
        # Cualquier otro error.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error inesperado al actualizar el comentario")

    # Construimos la respuesta final.
    response = CommentResponse.model_validate(comment)
    response.author_name = current_user.name
    response.author_email = current_user.email
    return response

# ---------------------------------------------------------------------------
# Eliminar comentario
# ---------------------------------------------------------------------------

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un comentario siempre que el usuario sea su propietario.

    Flujo:
    1. Verificación de existencia
    2. Verificación de propiedad
    3. Eliminación
    4. Manejo de errores con rollback
    """
    try:
        # Verificamos que exista.
        comment = get_comment_or_404(comment_id, db)

        # Verificamos que el usuario autenticado sea el dueño.
        check_comment_owner(comment, current_user)

        # Procedemos con la eliminación.
        db.delete(comment)
        db.commit()

    except HTTPException:
        # Errores establecidos (404/403) se relanzan.
        raise

    except SQLAlchemyError:
        # Error SQL durante DELETE/COMMIT.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al eliminar el comentario")

    except Exception:
        # Error general inesperado.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error inesperado al eliminar el comentario")

    return None

# ---------------------------------------------------------------------------
# Eliminar todos mis comentarios
# ---------------------------------------------------------------------------

@router.delete("/me/all", status_code=status.HTTP_200_OK)
def delete_all_my_comments(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina todos los comentarios del usuario autenticado.

    Flujo:
    1. Filtro por profile_id
    2. Eliminación en lote
    3. Confirmación con commit
    4. Manejo exhaustivo de errores
    """
    try:
        # Eliminamos con delete() directo para operaciones masivas.
        deleted_count = db.query(Comment).filter(
            Comment.profile_id == current_user.id
        ).delete(synchronize_session=False)

        # Guardamos los cambios.
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al eliminar tus comentarios")

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error inesperado al eliminar tus comentarios")

    return {
        "message": f"Se eliminaron {deleted_count} comentario(s)",
        "deleted_count": deleted_count
    }
