================================
Nested fields
================================

There are three meta fields which allow us to extend the handling of
both sides of a foreign key relationship (foreign key extras and many to
one extras), as well as many to many relationships.

Foreign key extras
~~~~~~~~~~~~~~~~~~

The ``foreign_key_extras`` field is a dictionary containing information
regarding how to handle a model's foreign keys. Here is an example:

.. code:: python

    class Cat(models.Model):
        owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cats")
        name = models.TextField(

    class CreateCatMutation(DjangoCreateMutation):
        class Meta:
            model = Cat
            foreign_key_extras = {"owner": {"type": "CreateUserInput"}}

By default, the ``owner`` field is of type ``ID!``, i.e. you have to
supply the ID of an owner when creating a cat. But suppose you instead
for every cat want to create a new user as well. Well that's exactly
what this mutation allows for (demands).

Here, the ``owner`` field will now be of type ``CreateUserInput!``,
which has to have been created before, typically via a
``CreateUserMutation``, which by default will result in the type name
``CreateUserInput``. An example call to the mutation is:

.. code:: graphql

    mutation {
        createCat(input: {owner: {name: "John Doe"}, name: "Kitty"}){
            cat{
                name
                owner {
                    id
                    name
                }
            }
        }
    }

A current TODO here is to allow the type to be ``auto``, which will
automatically create a new type. This is useful in cases where you don't
want to reuse an existing type.

Many to one extras
~~~~~~~~~~~~~~~~~~

The ``many_to_one_extras`` field is a dictionary containing information
regarding how to handle many to one relations, i.e. the "other" side of
a foreign key. Suppose we have the ``Cat`` model as above. Looking from
the User-side, we could add nested creations of Cat's, by the following
mutation

.. code:: python

    class CreateUserMutation(DjangoCreateMutation):
        class Meta:
            model = User
            many_to_one_extras = {
                "cats": {
                    "add": {"type": "auto"}
                }
            }

This will add an input argument ``catsAdd``, which accepts an array of
Cat objects. Note that the type value ``auto`` means that a new type to
accept the cat object will be created. This is usually necessary, as the
regular ``CreateCatInput`` requires an owner id, which we do not want to
give here, as it is inferred.

Now we could create a user with multiple cats in one go as follows:

.. code:: graphql

    mutation {
        createUser(input: {
            name: "User",
            catsAdd: [
                {name: "First Kitty"},
                {name: "Second kitty"}
            ]
        }){
            user{
                id
                name
                cats{
                    edges{
                        node{
                            id
                        }
                    }
                }
            }
        }
    }

Note that the default many to one relation argument ``cats`` still
accepts a list of inputs. You might want to keep it this way. However,
you can override the default by adding an entry with the key "exact":

.. code:: python

    class CreateUserMutation(DjangoCreateMutation):
        class Meta:
            model = User
            many_to_one_extras = {
                "cats": {
                    "exact": {"type": "auto"}
                }
            }

Note that we can add a new key with the type "ID", to still allow for
Cat objects to be added by id.

.. code:: python

    class CreateUserMutation(DjangoCreateMutation):
        class Meta:
            model = User
            many_to_one_extras = {
                "cats": {
                    "exact": {"type": "auto"},
                    "by_id": {"type": "ID"}
                }
            }

.. code:: graphql

    mutation {
        createUser(input: {
            name: "User",
            cats: [
                {name: "First Kitty"},
                {name: "Second kitty"}
            ],
            catsById: ["Q2F0Tm9kZTox"]
        }){
            user{
                ...UserInfo
            }
        }
    }

Many to many extras
~~~~~~~~~~~~~~~~~~~

The ``many_to_one_extras`` field is a dictionary containing information
regarding how to handle many to many relations. Suppose we have the
``Cat`` model as above, and a ``Dog`` model like:

.. code:: python

    class Dog(models.Model):
        owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
        name = models.TextField()

        enemies = models.ManyToManyField(Cat, blank=True, related_name='enemies')

        def is_stray():
            return self.owner is None


    class DogNode(DjangoObjectType):
        class Meta:
            model = Dog

We now have a many to many relationship, which by default will be
modelled by default using an ``[ID]`` argument. However, this can be
customized fairly similar to many to one extras:

.. code:: python

    class CreateDogMutation(DjangoCreateMutation):
        class Meta:
            model = Dog
            many_to_many_extras = {
                'enemies': {
                    'add': {"type": "CreateCatInput"}
                }
            }

This will, similar to before, add an ``enemiesAdd`` argument:

.. code:: graphql

    mutation {
        createDog(input: {
            name: "Buster",
            enemies: ["Q2F0Tm9kZTox"],
            enemiesAdd: [{owner: "VXNlck5vZGU6MQ==", name: "John's cat"]
        }}){
            dog{
                ...DogInfo
            }
        }
    }

This will create a dog with two enemies, one that already exists, and a
new one, which has the owner ``VXNlck5vZGU6MQ==`` (some existing user).
Note that if ``CreateCatInput`` expects us to create a new user, we
would have to do that here.

We can also add an extra field here for removing entities from a many to
many relationship:

.. code:: python

    class UpdateDogMutation(DjangoUpdateMutation):
        class Meta:
            model = Dog
            many_to_many_extras = {
                "enemies": {
                    "add": {"type": "CreateCatInput"},
                    "remove": {"type": "ID"},
                    # A similar form would be "remove": true
                }
            }

Note that this *has* to have the type "ID". Also note that this has no
effect on ``DjangoCreateMutation`` mutations. We could then perform

.. code:: graphql

    mutation {
        updateDog(id: "RG9nTm9kZTox", input: {
            name: "Buster 2",
            enemiesRemove: ["Q2F0Tm9kZTox"],
            enemiesAdd: [{owner: "VXNlck5vZGU6MQ==", name: "John's cat"]
        }}){
            dog{
                ...DogInfo
            }
        }
    }

This would remove "Q2F0Tm9kZTox" as an enemy, in addition to creating a
new one as before.

We can alter the behaviour of the default argument (e.g. ``enemies``),
by adding the "exact":

.. code:: python

    class UpdateDogMutation(DjangoUpdateMutation):
        class Meta:
            model = Dog
            many_to_many_extras = {
                "enemies": {
                    "exact": {"type": "CreateCatInput"},
                    "remove": {"type": "ID"},
                    # A similar form would be "remove": true
                }
            }

.. code:: graphql

    mutation {
        updateDog(id: "RG9nTm9kZTox", input: {
            name: "Buster 2",
            enemies: [{owner: "VXNlck5vZGU6MQ==", name: "John's cat"]
        }}){
            dog{
                ...DogInfo
            }
        }
    }

This will have the rather odd behavior that all enemies are reset, and
only the new ones created will be added to the relationship. In other
words it exists as a sort of ``purge and create`` functionality. When
used in a ``DjangoCreateMutation`` it will simply function as an initial
populator of the relationship.

A TODO here is adding the type ``auto`` for many to many extras.

Other aliases
~~~~~~~~~~~~~

In both the many to many and many to one extras cases, the naming of the
extra fields are not arbitrary. However, they can be customized. Suppose
you want your field to be named ``enemiesKill``, which should remove
from a many to many relationship. Then initially, we might write:

.. code:: python

        class UpdateDogMutation(DjangoUpdateMutation):
            class Meta:
                model = Dog
                many_to_many_extras = {
                    "enemies": {
                        "exact": {"type": "CreateCatInput"},
                        "kill": {"type": "ID"},
                    }
                }

Unfortunately, this will not work, as graphene-django-cud does not know
what operation ``kill`` translates to. Should we add or remove (or set)
the entities? Fortunately, we can explicitly tell which operation to
use, by supplying the "operation" key:

.. code:: python

    class UpdateDogMutation(DjangoUpdateMutation):
        class Meta:
            model = Dog
            many_to_many_extras = {
                "enemies": {
                    "exact": {"type": "CreateCatInput"},
                    "kill": {"type": "ID", "operation": "remove"},
                }
            }

Legal values are "add", "remove", and "update" (and some aliases of
these).

The argument names can also be customized:

.. code:: python

    class UpdateDogMutation(DjangoUpdateMutation):
        class Meta:
            model = Dog
            many_to_many_extras = {
                "enemies": {
                    "exact": {"type": "CreateCatInput"},
                    "kill": {"type": "ID", "operation": "remove", "name": "kill_enemies"},
                }
            }

The name of the argument will be ``killEnemies`` instead of the default
``enemiesKill``. The name will be translated from snake\_case to
camelCase as per usual.

Deep nested arguments
~~~~~~~~~~~~~~~~~~~~~

Note that deeply nested arguments are added by default when using
existing types. Hence, for the mutation

.. code:: python

    class CreateDogMutation(DjangoCreateMutation):
        class Meta:
            model = Dog
            many_to_many_extras = {
                "enemies": {
                    "exact": {"type": "CreateCatInput"},
                }
            }

Where ``CreateCatInput`` is the type generated for

.. code:: python

    class CreateCatMutation(DjangoCreateMutation):
        class Meta:
            model = Cat
            many_to_many_extras = {
                "targets": {"exact": {"type": "CreateMouseInput"}},
            }
            foreign_key_extras = {"owner": {"type": "CreateUserInput"}}

Where we assume we have now also created a new model ``Mouse`` with a
standard ``CreateMouseMutation`` mutation. We could then execute the following mutation:

.. code:: graphql

    mutation {
        createDog(input: {
            owner: null,
            name: "Spark",
            enemies: [
                {
                    name: "Kitty",
                    owner: {name: "John doe"},
                    targets: [
                        {name: "Mickey mouse"}
                    ]
                },
                {
                    name: "Kitty",
                    owner: {name: "Ola Nordmann"}
                }
            ]
       }){
            ...DogInfo
       }
    }

This creates a new (stray) dog, two new cats with one new owner each and
one new mouse. The new cats and the new dog are automatically set as
enemies, and the mouse is automatically set as a target of the first
cat.

For ``auto`` fields, we can create nested behaviour explicitly:

.. code:: python

    class CreateUserMutation(DjangoCreateMutation):
        class Meta:
            model = User
            many_to_one_extras = {
                "cats": {
                    "exact": {
                        "type": "auto",
                        "many_to_many_extras": {
                            "enemies": {
                                "exact": {
                                   "type": "CreateDogInput"
                                }
                            }
                        }
                    }
                }
            }

There is no limit to how deep this recursion may be.
