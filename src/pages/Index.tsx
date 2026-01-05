import { Navigate } from "react-router-dom";
import { ROUTES } from "@/lib/constants";

const Index = () => {
  return <Navigate to={ROUTES.LOGIN} replace />;
};

export default Index;
