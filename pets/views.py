from rest_framework.views import (
    APIView, Request, Response, status
)

from pets.serializer import PetSerializer
from .models import Pet
from groups.models import Group
from traits.models import Trait
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):

    def post(self, req: Request) -> Response:
        received_data = req.data
        serializer = PetSerializer(data=received_data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")

        group, created = Group.objects.get_or_create(
            scientific_name=group_data["scientific_name"]
        )

        pet = Pet.objects.create(
            **serializer.validated_data,
            group=group
        )

        for trait_data in traits_data:
            try:
                trait = Trait.objects.get(name__iexact=trait_data["name"])
            except Trait.DoesNotExist:
                trait = Trait.objects.create(**trait_data)
            
            pet.traits.add(trait)

        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, req: Request) -> Response:
        trait_param = req.query_params.get("trait", None)
        pets_list = Pet.objects.all()
        
        if trait_param:
            pets_list = pets_list.filter(traits__name=trait_param)

        result_page = self.paginate_queryset(pets_list, req, view=self)
        serializer = PetSerializer(result_page, many=True)
        
        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PetSerializer(found_pet)
        return Response(serializer.data)
    
    def patch(self, req: Request, pet_id: int) -> Response:
        
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        found_pet_serializer = PetSerializer(
            found_pet, data=req.data, partial=True
        )
        if not found_pet_serializer.is_valid():
            return Response(
                found_pet_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        group_data = found_pet_serializer.validated_data.pop("group", None)
        traits_data = found_pet_serializer.validated_data.pop("traits", None)

        for key, value in found_pet_serializer.validated_data.items():
            setattr(found_pet, key, value)
        
        if group_data:
            group, created = Group.objects.get_or_create(
                scientific_name=group_data["scientific_name"]
            )
            found_pet.group = group
        
        if traits_data:
            traits_list = []
            for trait_obj in traits_data:
                try:
                    trait = Trait.objects.get(name__iexact=trait_obj["name"])
                except Trait.DoesNotExist:
                    trait = Trait.objects.create(**trait_obj)
                
                traits_list.append(trait)

            found_pet.traits.set(traits_list)       

        found_pet.save()
        updated_serializer = PetSerializer(found_pet)
        return Response(updated_serializer.data)

    def delete(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        found_pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

