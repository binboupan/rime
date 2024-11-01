console.log("Load plugin.js")

function runPlugin(id){

    let element = document.getElementById("website_{{service}}");
    // const id = element.getAttribute("id")

    console.log(id)
    // async function pingService_{{service}}(){
    //     console.log("Pinging")
    //     try {
    //         const req = await fetch("/website/status?id={{service}}&category={{category}}")

    //         if(req.status === 200){
    //             element_{{service}}.classList.remove("website-red");    
    //             element_{{service}}.classList.add("website-green");     

    //         } else{
    //             element_{{service}}.classList.remove("website-green");    
    //             element_{{service}}.classList.add("website-red");

    //         }
    //         console.log(req)
    //     } catch (error) {
    //         console.log(error)
    //         element_{{service}}.classList.add("website-red");
    //     }
    // }

    // console.log(element_{{service}})
    // pingService_{{service}}()
    // setInterval(pingService_{{service}}, {{config[category][service]['interval']*1000}})



}

