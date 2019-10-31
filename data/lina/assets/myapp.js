d3.csv("./assets/North_carolina_drug_poisoning.csv").then((drugsdata) => {
   
    drugsdata.forEach(function(data){
        console.log(data)
        
    })
});