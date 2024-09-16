# def bike_rental_list(request):
#     # ... (существующий код)

#     applied_filters = {}
#     for key, value in request.GET.items():
#         if value and key != 'page' and key != 'advancedFiltersState':
#             applied_filters[key] = value

#     context = {
#         # ... (существующий контекст)
#         'applied_filters': applied_filters,
#     }

#     return render(request, 'bike_rental.html', context)
