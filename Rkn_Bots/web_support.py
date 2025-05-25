from aiohttp import web

HgBotz = web.RouteTableDef()

@HgBotz.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("HgBotz")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(HgBotz)
    return web_app
