import graphene
from graphene import Node, Schema
from graphene_django import DjangoObjectType, DjangoConnectionField

from graphene_django_cud.mutations import (
    DjangoCreateMutation,
    DjangoPatchMutation,
    DjangoUpdateMutation,
    DjangoDeleteMutation,
    DjangoBatchDeleteMutation, DjangoBatchCreateMutation, DjangoBatchPatchMutation)
from graphene_django_cud.tests.models import User, Cat, Dog, Mouse


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (Node,)


class CatNode(DjangoObjectType):
    class Meta:
        model = Cat
        interfaces = (Node,)


class DogNode(DjangoObjectType):
    class Meta:
        model = Dog
        interfaces = (Node,)


class MouseNode(DjangoObjectType):
    class Meta:
        model = Mouse
        interfaces = (Node,)


class Query(graphene.ObjectType):
    user = Node.Field(UserNode)
    cat = Node.Field(CatNode)
    dog = Node.Field(DogNode)
    mice = Node.Field(MouseNode)

    all_users = DjangoConnectionField(UserNode)
    all_cats = DjangoConnectionField(CatNode)
    all_dogs = DjangoConnectionField(DogNode)
    all_mice = DjangoConnectionField(MouseNode)


class CreateUserMutation(DjangoCreateMutation):
    class Meta:
        model = User
        many_to_one_extras = {
            "cats": {"exact": {"type": "auto"}},
            "dogs": {
                "add": {
                    "many_to_many_extras": {
                        "friends": {"add": {"type": "CreateMouseInput"}}
                    },
                }
            },
        }


class BatchCreateUserMutation(DjangoBatchCreateMutation):
    class Meta:
        model = User
        use_type_name = 'CreateUserInput'
        many_to_one_extras = {
            "cats": {"exact": {"type": "auto"}}
        }


class PatchUserMutation(DjangoPatchMutation):
    class Meta:
        model = User
        many_to_one_extras = {
            "cats": {"add": {"type": "CreateCatInput"}},
            "dogs": {
                "add": {
                    "many_to_many_extras": {
                        "friends": {"add": {"type": "CreateMouseInput"}}
                    },
                }
            },
        }

    @classmethod
    def mutate(cls, root, info, id, input):
        print(info)
        return super().mutate(root, info, id, input)


class UpdateUserMutation(DjangoUpdateMutation):
    class Meta:
        model = User


class DeleteUserMutation(DjangoDeleteMutation):
    class Meta:
        model = User


class CreateCatMutation(DjangoCreateMutation):
    class Meta:
        model = Cat
        many_to_many_extras = {
            "enemies": {"exact": {"type": "CreateDogInput"}},
            "targets": {"exact": {"type": "CreateMouseInput"}},
        }
        foreign_key_extras = {"owner": {"type": "CreateUserInput"}}


class UpdateCatMutation(DjangoUpdateMutation):
    class Meta:
        model = Cat
        many_to_many_extras = {
            "enemies": {
                "add": {
                    "type": "CreateDogInput",
                    "many_to_many_extras": {
                        "friends": {"add": True, "type": "CreateMouseInput"}
                    },
                },
                "remove": True,
                "exact": {"type": "ID"},
            }
        }
        foreign_key_extras = {"owner": {"type": "CreateUserInput"}}


class PatchCatMutation(DjangoPatchMutation):
    class Meta:
        model = Cat
        many_to_many_extras = {
            "enemies": {
                "add": {"type": "CreateDogInput"},
                "add_by_id": {"type": "ID", "operation": "add"},
                "remove": True,
            }
        }


class DeleteCatMutation(DjangoDeleteMutation):
    class Meta:
        model = Cat


class CreateDogMutation(DjangoCreateMutation):
    class Meta:
        model = Dog
        many_to_many_extras = {"friends": {"add": {"type": "CreateMouseInput"}}}


class PatchDogMutation(DjangoPatchMutation):
    class Meta:
        model = Dog
        many_to_many_extras = {
            "enemies": {
                "add": {"type": "CreateDogInput"},
                "remove": True,
                "exact": {"type": "ID"},
            }
        }


class BatchPatchDogMutation(DjangoBatchPatchMutation):
    class Meta:
        model = Dog


class UpdateDogMutation(DjangoUpdateMutation):
    class Meta:
        model = Dog


class DeleteDogMutation(DjangoDeleteMutation):
    class Meta:
        model = Dog


class CreateMouseMutation(DjangoCreateMutation):
    class Meta:
        model = Mouse


class PatchMouseMutation(DjangoPatchMutation):
    class Meta:
        model = Mouse


class UpdateMouseMutation(DjangoUpdateMutation):
    class Meta:
        model = Mouse


class DeleteMouseMutation(DjangoDeleteMutation):
    class Meta:
        model = Mouse


class BatchDeleteMouseMutation(DjangoBatchDeleteMutation):
    class Meta:
        model = Mouse
        filter_fields = (
            'id__in', 'name__contains', 'friends__owner__name'
        )


class Mutations(graphene.ObjectType):
    batch_create_user = BatchCreateUserMutation.Field()
    create_user = CreateUserMutation.Field()
    patch_user = PatchUserMutation.Field()
    update_user = UpdateUserMutation.Field()
    delete_user = DeleteUserMutation.Field()

    create_dog = CreateDogMutation.Field()
    patch_dog = PatchDogMutation.Field()
    update_dog = UpdateDogMutation.Field()
    delete_dog = DeleteDogMutation.Field()

    create_cat = CreateCatMutation.Field()
    patch_cat = PatchCatMutation.Field()
    update_cat = UpdateCatMutation.Field()
    delete_cat = DeleteCatMutation.Field()

    create_mouse = CreateMouseMutation.Field()
    patch_mouse = PatchMouseMutation.Field()
    update_mouse = UpdateMouseMutation.Field()
    delete_mouse = DeleteMouseMutation.Field()
    batch_delete_mouse = BatchDeleteMouseMutation.Field()


schema = Schema(query=Query, mutation=Mutations)
