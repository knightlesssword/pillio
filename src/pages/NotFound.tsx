import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Home, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/lib/constants";

const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md"
      >
        <div className="w-24 h-24 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-8">
          <span className="text-5xl">🔍</span>
        </div>
        <h1 className="text-4xl font-bold text-foreground mb-4">Page Not Found</h1>
        <p className="text-muted-foreground mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex gap-4 justify-center">
          <Button variant="outline" onClick={() => window.history.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </Button>
          <Button className="gradient-primary" asChild>
            <Link to={ROUTES.DASHBOARD}>
              <Home className="h-4 w-4 mr-2" />
              Dashboard
            </Link>
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default NotFound;
