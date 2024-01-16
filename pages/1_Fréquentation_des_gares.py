if choix_menu == "Carte":
        df1 = pd.read_csv("data/liste-des-gares.csv", sep=';')
        df2 = pd.read_csv("data/frequentation-gares.csv", sep=';')

        df1[['Latitude', 'Longitude']] = df1['Geo Point'].str.split(', ', expand=True)
        df1['Latitude'] = df1['Latitude'].astype(float)
        df1['Longitude'] = df1['Longitude'].astype(float)

        columns_to_keep = ['CODE_UIC','LIBELLE','COMMUNE','DEPARTEMEN','Latitude','Longitude']
        df1 = df1[columns_to_keep]

        columns_to_keep = ['Nom de la gare','Code UIC','Code postal','Segmentation DRG','Total Voyageurs 2022','Total Voyageurs 2021','Total Voyageurs 2020','Total Voyageurs 2019','Total Voyageurs 2018','Total Voyageurs 2017','Total Voyageurs 2016','Total Voyageurs 2015']
        df2 = df2[columns_to_keep]

        df = pd.merge(df2, df1, left_on='Code UIC', right_on='CODE_UIC', how='inner')
        center=[df1.Latitude.mean(), df1.Longitude.mean()]
        df['Nombre de gares'] = 1

        map = folium.Map(location=center, zoom_start=6, control_scale=True)

        on = st.toggle('Vision Détails Gares')
        
        annee = st.slider('Année', 2015, 2022)
        data1=df
        data1['Total Voyageurs'] = data1[f'Total Voyageurs {annee}']

        categ = st.radio('Nombre de Voyageurs',('Tous','Peu','Moyen','Beaucoup'))
        purpose_colour = {'0':'lightblue', '1':'blue', '2':'darkblue'}

        segmentation = st.selectbox('Type de gare',['Tous types de gares','Gares de voyageurs d’intérêt national','Gares de voyageurs d’intérêt régional','Gares de voyageurs d’intérêt local'])
        data2=data1
        if segmentation == 'Gares de voyageurs d’intérêt national':
            data2 = data2[data2['Segmentation DRG'] == 'A']
        elif segmentation == 'Gares de voyageurs d’intérêt régional':
            data2 = data2[data2['Segmentation DRG'] == 'B']
        elif segmentation == 'Gares de voyageurs d’intérêt local':
            data2 = data2[data2['Segmentation DRG'] == 'C']
        else:
            data2=data1

        col1, col2 = st.columns(2)

        if on:
            data3=data2
            data3['Total Voyageurs'] = data3['Total Voyageurs'].astype(int)
            data3['Catégorie'] = pd.qcut(data3['Total Voyageurs'], 3, labels=False)
            data3["Catégorie"] = data3["Catégorie"].astype(str)

            data4=data3
            if categ == 'Peu':
                data4=data4[(data4['Catégorie']== '0')]
            elif categ == 'Moyen':
                data4=data4[(data4['Catégorie']== '1')]
            elif categ == 'Beaucoup':
                data4=data4[(data4['Catégorie']== '2')]
            else:
                data4=data3
            
            col1.metric("Nombre de Gares", len(data4))
            col2.metric("Nombre de Voyageurs", sum(data4['Total Voyageurs']))

            for i,row in data4.iterrows():
                content = f'Département: {str(row["DEPARTEMEN"])}<br>' f'Gare: {str(row["Nom de la gare"])}<br>' f'Total Voyageurs: {str(row["Total Voyageurs"])}'
                iframe = folium.IFrame(content, width=400, height=100)
                popup = folium.Popup(iframe, min_width=400, max_width=400)
            
                try:
                    icon_color = purpose_colour[row['Catégorie']]
                except:
                    icon_color = 'gray'
            
                folium.Marker(location=[row['Latitude'],row['Longitude']],
                            popup = popup, 
                            icon=folium.Icon(color=icon_color, icon='')).add_to(map)

        else:
            data3=data2
            data3=data3.groupby('DEPARTEMEN').agg({
            'Longitude': 'mean',
            'Latitude': 'mean',
            'Total Voyageurs': 'sum',
            'Nombre de gares': 'sum'
            }).reset_index()

            data3['Total Voyageurs'] = data3['Total Voyageurs'].astype(int)
            data3['Catégorie'] = pd.qcut(data3['Total Voyageurs'], 3, labels=False)
            data3["Catégorie"] = data3["Catégorie"].astype(str)

            data4=data3
            if categ == 'Small':
                data4=data4[(data4['Catégorie']== '0')]
            elif categ == 'Medium':
                data4=data4[(data4['Catégorie']== '1')]
            elif categ == 'Large':
                data4=data4[(data4['Catégorie']== '2')]
            else:
                data4=data3
            
            col1.metric("Nombre de Gares", sum(data4['Nombre de gares']))
            col2.metric("Nombre de Voyageurs", sum(data4['Total Voyageurs']))

            for i,row in data4.iterrows():
                content = f'Département: {str(row["DEPARTEMEN"])}<br>' f'Total Voyageurs: {str(row["Total Voyageurs"])}<br>' f'Nombre de Gares: {str(row["Nombre de gares"])}'
                iframe = folium.IFrame(content, width=400, height=100)
                popup = folium.Popup(iframe, min_width=400, max_width=400)
            
                try:
                    icon_color = purpose_colour[row['Catégorie']]
                except:
                    icon_color = 'gray'
            
                folium.Marker(location=[row['Latitude'],row['Longitude']],
                            popup = popup, 
                            icon=folium.Icon(color=icon_color, icon='')).add_to(map)

        st_data = st_folium(map, width=800)
