using Microsoft.Owin;
using Owin;

[assembly: OwinStartupAttribute(typeof(ivetappedthat.Startup))]
namespace ivetappedthat
{
    public partial class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            ConfigureAuth(app);
        }
    }
}
