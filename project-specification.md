# Project - Dobble-generator 

 ## Project goal

  - develop a nice we application for generation of cards for cards game called dobble
  - follow standard dobble logic and rules ( number of cards, number of symbols )
  - to generated final pdf document that will contain two cars per page, to be printed and laminated ( use well the space on A4 paper )

### features
 - library management 
  - support of creation of new "dobble type " by importing a new set of images 
  - support "cartonize feature" feature for library of images / symbols in that library
  - support flexibly various sources of images, 
        - json file with links and metadata
        - API
        - direct upload of images 
 - print dobble game / send dobble game
 - display dobble agem 
    
### stack
 - Svelte and Material UI webc component ( https://m3.material.io/develop/web )
 - Typescript for frontent 
 - Python as backbone backend - fast api
  

#### Resource for images 
 - app should create a simple library by dobble type ( harry potter and other themes - to be defined by a user  - by specifiing source image library ) 
 - original api 
https://github.com/KostaSav/hp-api/blob/master/data/characters.json
 - images to be fetched to app assets and to be "cartoonized"