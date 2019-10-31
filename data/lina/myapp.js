d3.csv("./North_carolina_drug_poisoning", function(err,drugdata){
    if(err) throw err;
    drugdata.forEach(function(data){
        console.log(data)
    })
})