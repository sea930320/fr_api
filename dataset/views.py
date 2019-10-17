from .models import Dataset, Image
from .serializers import DatasetSerializer
from authentication.serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, CreateAPIView, DestroyAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView


class DatasetRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DatasetSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user.dataset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def update(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(request.user.dataset, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def destroy(self, request, *args, **kwargs):
    #     try:
    #         dataset = Dataset.objects.get(pk=int(kwargs['pk']), user_id=request.user.id)
    #     except Exception as e:
    #         raise NotFound('dataset not found')
    #
    #     dataset.delete()
    #
    #     return Response({
    #         'msg': 'dataset successfully removed',
    #     }, status=status.HTTP_200_OK)

# class DatasetCreateAPIView(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = DatasetSerializer
#
#     def post(self, request):
#         data = request.data
#         data.update({'user_id': request.user.pk})
#         # The create serializer, validate serializer, save serializer pattern
#         # below is common and you will see it a lot throughout this course and
#         # your own work later on. Get familiar with it.
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhotoAddAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DatasetSerializer
    user_seriralizer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        dataset = request.user.dataset
        data = {"image": request.data}
        serializer = self.serializer_class(dataset, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer = self.user_seriralizer_class(request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhotoRemoveAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DatasetSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            img = Image.objects.get(pk=int(kwargs['pk']), image_dataset=request.user.dataset)
        except Exception as e:
            raise NotFound('image not found')
        img.delete()

        serializer = self.serializer_class(request.user.dataset)
        return Response({
            'msg': 'photo successfully removed',
            'dataset': serializer.data
        }, status=status.HTTP_200_OK)
